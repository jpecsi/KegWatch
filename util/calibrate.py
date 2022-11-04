#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import time, os
import RPi.GPIO as GPIO 
from datetime import datetime
from datetime import date
import paho.mqtt.client as mqtt
import configparser
import mysql.connector



# ========== FUNCTIONS ========== #
# Write to the database
def write_to_db(q,v):
    try:
        # Connect to Database
        db_server = mysql.connector.connect(
            host=config['database']['host'],
            port=config.getint("database","port"),
            user=config['database']['username'],
            password=config['database']['password'],
            database=config['database']['database']
        )

        # Cursor to execute SQL
        db = db_server.cursor()

        # Write to the database
        db.execute(q,v)
        db_server.commit()

    except Exception as e:
        print("[" + str(datetime.now()) + "] DATABASE ERROR: " + str(e))

    # Close the connection
    db.close()
    db_server.close()



def read_db(q,v):
    try:
        # Connect to Database
        db_server = mysql.connector.connect(
            host=config['database']['host'],
            port=config.getint("database","port"),
            user=config['database']['username'],
            password=config['database']['password'],
            database=config['database']['database']
        )

        # Cursor to execute SQL
        db = db_server.cursor()

        # Write to the database
        results = []
        db.execute(q,v)
        for row in db:
            results.append(row)
        
    except Exception as e:
        print("DATABASE ERROR: " + str(e))

    # Close the connection
    db.close()
    db_server.close()
    return results



# Tap 1 Handler
def tap1(channel):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:  
        t1_start = time.perf_counter()     # Start the timer
        GPIO.output(t1_led,GPIO.LOW)       # Turn on the tap's LED
      
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t1_end = time.perf_counter()        # Stop the timer
        GPIO.output(t1_led,GPIO.HIGH)       # Turn off the tap's LED
        calc_beer(1,(t1_end - t1_start))    # Calculate the remaining beer
        
        

# Tap 2 Handler
def tap2(channel):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t2_start = time.perf_counter()      # Start the timer
        GPIO.output(t2_led,GPIO.LOW)        # Turn on the tap's LED
        
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t2_end = time.perf_counter()        # Stop the timer
        GPIO.output(t2_led,GPIO.HIGH)       # Turn off the tap's LED
        calc_beer(2,(t2_end - t2_start))    # Calculate the remaining beer



# Calculate Beer Remaining
def calc_beer(t,s):
    # Get current time to report "last pour time"
    now = datetime.now()

    # Get flow rate
    flow_rate = oz/s

    # Get tap information
    db_data = read_db("SELECT id,name,abv,remaining,date_tapped FROM keg_log WHERE tap=%s AND status=1", (t,))

    # Proceed if the tap is active...
    if len(db_data) == 1:
        # Get current tap data
        tap = {
            "beer_id": db_data[0][0],
            "beer_name": db_data[0][1],
            "abv": db_data[0][2],
            "remaining": db_data[0][3],
            "date_tapped": db_data[0][4],
        }

        consumer = "Calibration"
        
        # Figure out how much beer was poured / remains
        beer_poured = oz
        beer_remaining = round((tap["remaining"] - beer_poured),2)

        # Don't allow remaining to go negative
        if beer_remaining < 0:
            beer_remaining = 0

        # Update beer remaining
        if beer_remaining == 0:
            # Calcualte how many days since the keg was tapped
            today = date(datetime.now().year,datetime.now().month,datetime.now().day)
            tapped = tap["date_tapped"].split("-")
            tapped_date = date(int(tapped[0]),int(tapped[1]),int(tapped[2]))
            delta = today-tapped_date

            # Write to database
            write_to_db("UPDATE keg_log SET remaining=0,date_kicked=%s,days_to_consume=%s,status=0 WHERE id=%s", (today,delta.days,tap["beer_id"]))

         # Log in database
        write_to_db("INSERT INTO beer_log (time,tap_id,beer_id,beer_name,consumer,oz_poured) VALUES (%s,%s,%s,%s,%s,%s)", (now,t,tap["beer_id"],tap["beer_name"],consumer,beer_poured))
        write_to_db("UPDATE keg_log SET remaining=%s WHERE id=%s",(beer_remaining,tap["beer_id"]))

        # Update the flow rate
        tap_conf_id = ("tap_" + str(t))
        config.set(tap_conf_id, 'flow_rate', str(flow_rate))
        with open(cf, 'w') as configfile:
            config.write(configfile)

        # Update MQTT
        mqtt_publish(tap)

        # All done, exit
        print("\n[" + str(datetime.now()) + "] TAP " + str(t) + " FLOW RATE = " + str(flow_rate) + " oz/sec")
        exit()

# Push data to Home Assistant via MQTT
def mqtt_publish(t):
    # Make sure MQTT is enabled
    if (config.getboolean("mqtt_broker", "enabled")):
        # Connect to MQTT Server
        m_client = mqtt.Client(config['mqtt_broker']['client_id'])
        m_client.username_pw_set(username=config['mqtt_broker']['username'],password=config['mqtt_broker']['password'])
        m_client.connect(config['mqtt_broker']['host'],config.getint("mqtt_broker","port"))

        # Convert oz to "beers"
        beers_rem = round(t["remaining"]/12,1)

        # Build topic strings
        root_topic = config['mqtt_topics']["root_topic"] + "/t" + str(t) + "-"

        # Publish Data
        m_client.publish((root_topic+config['mqtt_topics']["beer_topic"]),t["beer"])
        m_client.publish((root_topic+config['mqtt_topics']["keg_capacity_topic"]),t["capacity"])
        m_client.publish((root_topic+config['mqtt_topics']["keg_remain_topic"]),t["remaining"])
        m_client.publish((root_topic+config['mqtt_topics']["beers_remain_topic"]),beers_rem)



# Startup LED Routine to indicate system running
def startup_routine():
    for t in range(4):
        GPIO.output(t1_led,GPIO.HIGH)
        GPIO.output(t2_led,GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(t1_led,GPIO.LOW)
        GPIO.output(t2_led,GPIO.LOW)
        time.sleep(0.2)
        



# ========== MAIN ========== #
if __name__ == '__main__':

    # Set working directory
    cf_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config'))
    cf = cf_path + "/settings.conf"

    # Read config and beer files
    config = configparser.ConfigParser()
    config.read(cf)

    # Hardware Configuration
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Tap 1
    t1_gpio = config.getint("tap_1","switch_gpio")                              # Reed switch GPIO pin
    t1_led = config.getint("tap_1","led_gpio")                                  # LED GPIO Pin
    GPIO.setup(t1_gpio,GPIO.IN)                                                 # Configure the switch
    GPIO.setup(t1_led,GPIO.OUT)                                                 # Configure the LED

    # Tap 2
    t2_gpio = config.getint("tap_2","switch_gpio")                              # Reed switch GPIO pin
    t2_led = config.getint("tap_2","led_gpio")                                  # LED GPIO pin
    GPIO.setup(t2_gpio,GPIO.IN)                                                 # Configure the switch
    GPIO.setup(t2_led,GPIO.OUT)                                                 # Configure the LED

    try:
        # Present Menu
        print("\n[KegWatch Calibration]\n======================\n")
        selected_tap = input("Which tap will be used to calibrate (1/2)? ")
        oz_input = input("How many oz are you pouring? ")
        oz = float(oz_input)


        # Create Event Detection
        if selected_tap == "1":
            # Check to see if tap is open before continuing
            if GPIO.input(t1_gpio) == 1:
                open_tap = 1
                print("Tap 1 is Open - Please Close to Continue")
                while open_tap == 1:
                    if GPIO.input(t1_gpio) == 0:
                        open_tap = 0

            # Add event handler and turn on LED
            GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=100) 
            GPIO.output(t1_led,GPIO.HIGH)
            GPIO.output(t2_led,GPIO.LOW)

        if selected_tap == "2":
            # Check to see if tap is open before continuing
            if GPIO.input(t2_gpio) == 1:
                open_tap = 1
                print("Tap 2 is Open - Please Close to Continue")
                while open_tap == 1:
                    if GPIO.input(t2_gpio) == 0:
                        open_tap = 0

            # Add event handler and turn on LED
            GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=100)
            GPIO.output(t2_led,GPIO.HIGH)
            GPIO.output(t1_led,GPIO.LOW)

        run = input("[" + str(datetime.now()) + "] BEGIN POURING ON TAP " + str(selected_tap)) 
    except KeyboardInterrupt:
        print("\n[" + str(datetime.now()) + "] EXITING")