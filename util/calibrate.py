#!/usr/bin/env python3

# ========== LIBRARIES ========== #
from re import S
import time, os
import RPi.GPIO as GPIO 
from datetime import datetime
from datetime import date
import paho.mqtt.client as mqtt
from threading import Thread
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
            database=config['database']['db_name']
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



# Tap 1 Handler
def tap1(channel):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:  
        t1_start = time.perf_counter()      # Start the timer
        GPIO.output(t1_led,GPIO.LOW)        # Turn off the tap's LED
      
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t1_end = time.perf_counter()        # Stop the timer
        GPIO.output(t1_led,GPIO.HIGH)       # Turn on the tap's LED
        calc_beer(1,(t1_end - t1_start))    # Calculate the remaining beer
        
        

# Tap 2 Handler
def tap2(channel):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t2_start = time.perf_counter()      # Start the timer
        GPIO.output(t2_led,GPIO.LOW)        # Turn off the tap's LED
        
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t2_end = time.perf_counter()        # Stop the timer
        GPIO.output(t2_led,GPIO.HIGH)       # Turn on the tap's LED
        calc_beer(2,(t2_end - t2_start))    # Calculate the remaining beer



# Calculate Beer Remaining
def calc_beer(t,s):
    # Get current time to report "last pour time"
    now = datetime.now()

    # Calculate the flow rate
    flow_rate = oz/s

    # Get current tap data
    tap = {
        "beer": config[taps[t]]['beer_name'],
        "remaining": config.getfloat(taps[t],"keg_remaining"),
        "tapped": config[taps[t]]['date_tapped']
    }
    
    # Figure out how much beer was poured / remains
    beer_remaining = round((tap["remaining"] - oz),2)

    # Update settings.conf
    config.set(taps[t], 'keg_remaining', str(beer_remaining))
    config.set(taps[t], 'flow_rate', str(flow_rate))
    with open(cf, 'w') as configfile:
        config.write(configfile)

    # Log in database
    write_to_db("INSERT INTO beer_log (time,tap,beer_name,oz_poured,consumer,oz_remain,date_tapped) VALUES (%s,%s,%s,%s,%s,%s,%s)",(now,t,tap["beer"],oz,"Calibration",beer_remaining,tap["tapped"]))
    
    # Update MQTT
    mqtt_publish(t)
    


# Push data to Home Assistant via MQTT
def mqtt_publish(t):
    # Connect to MQTT Server
    m_client = mqtt.Client(config['mqtt_broker']['client_id'])
    m_client.username_pw_set(username=config['mqtt_broker']['username'],password=config['mqtt_broker']['password'])
    m_client.connect(config['mqtt_broker']['host'],config.getint("mqtt_broker","port"))

    # Load data
    tap = {
        "beer": config[taps[t]]['beer_name'],
        "capacity": config.getfloat(taps[t],"keg_capacity"),
        "remaining": config.getfloat(taps[t],"keg_remaining"),
        "flow": config.getfloat(taps[t],"flow_rate"),
    }

    # Convert oz to "beers"
    beers_rem = round(tap["remaining"]/12,1)

    # Build topic strings
    root_topic = config['mqtt_topics']["root_topic"] + "/" + config[taps[t]]["mqtt_topic_id"] + "-"

    # Publish Data
    m_client.publish((root_topic+config['mqtt_topics']["beer_topic"]),tap["beer"])
    m_client.publish((root_topic+config['mqtt_topics']["keg_capacity_topic"]),tap["capacity"])
    m_client.publish((root_topic+config['mqtt_topics']["keg_remain_topic"]),tap["remaining"])
    m_client.publish((root_topic+config['mqtt_topics']["beers_remain_topic"]),beers_rem)


        


# ========== MAIN ========== #
if __name__ == '__main__':

    # Set working directory
    cf_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config'))
    cf = cf_path + "/settings.conf"

    # Read config and beer files
    config = configparser.ConfigParser()
    config.read(cf)

    # Collection of taps
    taps = {
        1: "tap_1",
        2: "tap_2"
    }

    # Hardware Configuration
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Tap 1
    t1_gpio = config.getint("tap_1","switch_gpio")                              # Reed switch GPIO pin
    t1_led = config.getint("tap_1","led_gpio")                                  # LED GPIO Pin
    GPIO.setup(t1_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)                        # Configure the switch
    GPIO.setup(t1_led,GPIO.OUT)                                                 # Configure the LED

    # Tap 2
    t2_gpio = config.getint("tap_2","switch_gpio")                              # Reed switch GPIO pin
    t2_led = config.getint("tap_2","led_gpio")                                  # LED GPIO pin
    GPIO.setup(t2_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)                        # Configure the switch
    GPIO.setup(t2_led,GPIO.OUT)                                                 # Configure the LED

    # Present Menu
    print("\n[KegWatch Calibration]\n======================\n")
    selected_tap = input("Which tap will be used to calibrate (1/2)? ")
    oz_input = input("How many oz are you pouring? ")
    oz = float(oz_input)

    # Create Event Detection
    if selected_tap == "1":
        GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300) 
        GPIO.output(t1_led,GPIO.HIGH)
    if selected_tap == "2":
        GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300)
        GPIO.output(t2_led,GPIO.HIGH)

    run = input("[" + str(datetime.now()) + "] BEGIN POURING ON TAP " + str(selected_tap)) 






