#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import pymongo
import time
import RPi.GPIO as GPIO 
from datetime import datetime
import paho.mqtt.client as mqtt
from threading import Thread
import configparser
import mysql.connector



# ========== FUNCTIONS ========== #
# Dirty, hacky way to keep the sensor code running
def persist():
    while True:
        time.sleep(1)

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

    # Who poured the beer?
    cup_id = config.getint("dev","cup_id")
    cup_query = 'SELECT user_id FROM cup_inventory WHERE id=%s'
    db.execute(cup_query,(cup_id,))
    for r in db:
        uid = r[0]

    consumer_query = 'SELECT first_name,last_name FROM consumers WHERE id=%s'
    db.execute(consumer_query,(uid,))
    for u in db:
        consumer = u[0] + " " + u[1]


    # Get current tap data
    tap = {
        "beer": config[taps[t]]['beer_name'],
        "remaining": config.getfloat(taps[t],"keg_remaining"),
        "flow": config.getfloat(taps[t],"flow_rate"),
        "tapped": config[taps[t]]['date_tapped']
    }

    # Figure out how much beer was poured
    beer_poured = s * tap["flow"]

    # Figure out how much beer remains in the keg after last pour
    beer_remaining = round((tap["remaining"] - beer_poured),2)

    # Don't allow remaining to go negative
    if beer_remaining < 0:
        beer_remaining = 0
    
    # Update beer remaining
    config.set(taps[t], 'keg_remaining', str(beer_remaining))
    with open('/opt/sensor/setup/settings.conf', 'w') as configfile:
        config.write(configfile)
    
    # Log the pour
    beer_log_query = ("INSERT INTO beer_log (time,tap,beer_name,oz_poured,consumer,oz_remain,date_tapped) VALUES (%s,%s,%s,%s,%s,%s,%s)")
    db.execute(beer_log_query,(now,t,tap["beer"],beer_poured,consumer,beer_remaining,tap["tapped"]))
    db_server.commit()

    # Update MQTT
    mqtt_publish(t)



# Push data to Home Assistant via MQTT
def mqtt_publish(t):
    # Connect to MQTT Server
    m_client = mqtt.Client(mqtt_settings["client_id"])
    m_client.username_pw_set(username=mqtt_settings["user"],password=mqtt_settings["pass"])
    m_client.connect(mqtt_settings["broker"],mqtt_settings["port"])

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
    root_topic = mqtt_topics["root"] + "/" + config[taps[t]]["mqtt_topic_id"] + "-"

    # Publish Data
    m_client.publish((root_topic+mqtt_topics["beer_name"]),tap["beer"])
    m_client.publish((root_topic+mqtt_topics["keg_capacity"]),tap["capacity"])
    m_client.publish((root_topic+mqtt_topics["keg_remaining"]),tap["remaining"])
    m_client.publish((root_topic+mqtt_topics["beers_remaining"]),beers_rem)



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

    # ===== LOAD CONFIGURATION ===== #
    # Read config and beer files
    config = configparser.ConfigParser()
    config.read('/opt/sensor/setup/settings.conf')

    # Collection of taps
    taps = {
        1: "tap_1",
        2: "tap_2"
    }



    # === GET REMAINING CONFIG ITEMS === #
    # Database
    db_settings = {
        "host": config['database']['host'],
        "port": config.getint("database","port"),
        "user": config['database']['username'],
        "pass": config['database']['password'],
        "database": config['database']['db_name']
    }


    # MQTT Broker
    mqtt_settings = {
        "broker": config['mqtt_broker']['host'],
        "port": config.getint("mqtt_broker","port"),
        "user": config['mqtt_broker']['username'],
        "pass": config['mqtt_broker']['password'],
        "client_id": config['mqtt_broker']['client_id'] 
    }

    # MQTT Topics
    mqtt_topics = {
        "root": config['mqtt_topics']["root_topic"],
        "beer_name": config['mqtt_topics']["beer_topic"],
        "keg_capacity": config['mqtt_topics']["keg_capacity_topic"],
        "keg_remaining": config['mqtt_topics']["keg_remain_topic"],
        "beers_remaining": config['mqtt_topics']["beers_remain_topic"]
    }



    # ===== SETUP ===== #
    # Hardware Configuration
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Tap 1
    t1_gpio = config.getint("tap_1","switch_gpio")              # Reed switch GPIO pin
    t1_led = config.getint("tap_1","led_gpio")                  # LED GPIO Pin
    GPIO.setup(t1_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)        # Configure the switch
    GPIO.setup(t1_led,GPIO.OUT)                                 # Configure the LED
    GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300)    # Handler to listen for switch

    # Tap 2
    t2_gpio = config.getint("tap_2","switch_gpio")              # Reed switch GPIO pin
    t2_led = config.getint("tap_2","led_gpio")                  # LED GPIO pin
    GPIO.setup(t2_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)        # Configure the switch
    GPIO.setup(t2_led,GPIO.OUT)                                 # Configure the LED
    GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300)    # Handler to listen for switch

    # Connect to Database
    db_server = mysql.connector.connect(
        host=db_settings["host"],
        port=db_settings["port"],
        user=db_settings["user"],
        password=db_settings["pass"],
        database=db_settings["database"]
    )

    # Cursor to execute SQL
    db = db_server.cursor()
    
    # Run Startup Indication
    startup_routine()

    # Persist Service
    p_thread = Thread(target=persist)
    p_thread.start()