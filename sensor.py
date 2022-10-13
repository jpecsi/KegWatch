#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import time, os
import RPi.GPIO as GPIO 
from datetime import datetime
from datetime import date
import paho.mqtt.client as mqtt
from threading import Thread
import configparser
import mysql.connector
import evdev
from evdev import InputDevice, categorize


# ========== FUNCTIONS ========== #
# Thread to read barcode input (continuously)
def scan_barcode():

    # ASCII Scan Codes (lowercase)
    scancodes = {
        0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
        10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
        20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
        30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
        40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
        50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 57: u' ', 100: u'RALT'
    }

    # ASCII Scan Codes (uppercase)
    capscodes = {
        0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
        10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
        20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
        30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
        40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
        50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT',  57: u' ', 100: u'RALT'
    }
   
    # Setup starting variables
    global cuser
    cuser = "Anonymous"
    temp = ""
    caps = False

    # Grab the barcode scanner (exclusively)
    dev.grab()
  
    # Run a loop looking for key presses
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            data = evdev.categorize(event)  # Save the event temporarily to introspect it
            # Only grab "down" presses; identify if lower/uppercase character
            if data.scancode == 42:  # Down events only
                if data.keystate == 1:
                    caps = True
                if data.keystate == 0:
                    caps = False
            if data.keystate == 1:  # Down events only
                if caps:
                    key_lookup = u'{}'.format(capscodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                else:
                    key_lookup = u'{}'.format(scancodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                if (data.scancode != 42) and (data.scancode != 28):
                    temp += key_lookup  
                if(data.scancode == 28):
                    # Set the user to the scanned ID, reset the temp/builder string
                    cuser=temp
                    temp=""

                    # Catch game-mode barcodes
                    if cuser[0] == '0':
                        if config.getboolean("game_mode", "enabled"):
                            game_logic(cuser[1:],"Mixed Drink",8,config.getfloat("game_mode","average_abv"))



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



# Put together the proper data for game sessions
def game_logic(c,t,q,p):
    # Get the active game id
    game = read_db("SELECT id FROM games WHERE status=%s", (1,))
    game = game[0][0]

    # Get current time
    now = datetime.now()
    
    # Get the team name (if there is one)
    team = read_db("SELECT team FROM teams WHERE consumer=%s AND game=%s", (c,game))
    if len(team) == 0:
        team = "None"
    else:
        team = team[0][0]

    # Log the drink to the game table
    write_to_db("INSERT INTO game_log (game,time,consumer,type_consumed,amount_consumed,bev_abv,team) VALUES (%s,%s,%s,%s,%s,%s,%s)", (game,now,c,t,q,p,team))



# Tap 1 Handler
def tap1(channel):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:  
        t1_start = time.perf_counter()      # Start the timer
        GPIO.output(t1_led,GPIO.HIGH)       # Turn on the tap's LED
      
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t1_end = time.perf_counter()        # Stop the timer
        GPIO.output(t1_led,GPIO.LOW)        # Turn off the tap's LED
        calc_beer(1,(t1_end - t1_start))    # Calculate the remaining beer
        
        

# Tap 2 Handler
def tap2(channel):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t2_start = time.perf_counter()      # Start the timer
        GPIO.output(t2_led,GPIO.HIGH)       # Turn on the tap's LED
        
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t2_end = time.perf_counter()        # Stop the timer
        GPIO.output(t2_led,GPIO.LOW)        # Turn off the tap's LED
        calc_beer(2,(t2_end - t2_start))    # Calculate the remaining beer



# Calculate Beer Remaining
def calc_beer(t,s):
    # Get current time to report "last pour time"
    now = datetime.now()

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
            "flow": config.getfloat(("tap_"+str(t)),"flow_rate"),
        }

        global cuser
        if len(cuser) < 1:
            cuser = "Anonymous"
        consumer = cuser
        cuser = "Anonymous"
        
        # Figure out how much beer was poured / remains
        beer_poured = s * tap["flow"]
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

        # If game mode is enabled...
        if config.getboolean("game_mode", "enabled"):
            drink_type = ("(Beer) " + tap["beer_name"])
            game_logic(consumer,drink_type,beer_poured,tap["abv"])

        # Update MQTT
        mqtt_publish(tap)

    

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
    cf_path = (os.path.realpath(os.path.dirname(__file__)))
    cf = cf_path + "/config/settings.conf"

    # Read config and beer files
    config = configparser.ConfigParser()
    config.read(cf)

    # Hardware Configuration
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Tap 1
    t1_gpio = config.getint("tap_1","switch_gpio")                              # Reed switch GPIO pin
    t1_led = config.getint("tap_1","led_gpio")                                  # LED GPIO Pin
    GPIO.setup(t1_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)                        # Configure the switch
    GPIO.setup(t1_led,GPIO.OUT)                                                 # Configure the LED
    GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300)     # Handler to listen for switch

    # Tap 2
    t2_gpio = config.getint("tap_2","switch_gpio")                              # Reed switch GPIO pin
    t2_led = config.getint("tap_2","led_gpio")                                  # LED GPIO pin
    GPIO.setup(t2_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)                        # Configure the switch
    GPIO.setup(t2_led,GPIO.OUT)                                                 # Configure the LED
    GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300)     # Handler to listen for switch

    # Grab the barcode scanner
    dev_path = "/dev/input/" + config.get("hardware","barcode_dev")
    dev = InputDevice(dev_path)

    # Thread for barcode input
    i_thread = Thread(target=scan_barcode)
    i_thread.start()

    # Run Startup Indication
    startup_routine()