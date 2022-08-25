#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import pymongo
import time
import RPi.GPIO as GPIO 
from datetime import datetime
import paho.mqtt.client as mqtt





# ========== FUNCTIONS ========== #
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

    # Get calibration data from db (how many oz pour per second)
    cal_query = conf_col.find({"config":"hardware"},{})
    for c in cal_query:
        oz_per_sec = c['oz_per_second']

    # Figure out how much beer was poured
    beer_poured = s * oz_per_sec

    # Get data from db (how much beer was in the keg before last pour)
    beer_query = beer_col.find({"_id":t},{})
    for b in beer_query:
        curr_beer_remaining = b['keg_oz_remaining']
        curr_beer_name = b['beer_name']

    # Figure out how much beer remaings in the keg after last pour
    beer_remaining = round((curr_beer_remaining - beer_poured),2)
    
    # Update the database (beer remaining)
    beer_col.update_one({"_id":t},{"$set":{"keg_oz_remaining":beer_remaining}})
    beer_col.update_one({"_id":t},{"$set":{"last_pour":str(now)}})

    # Create a new record for the "consumption" collection
    consumption_record = {  "_id": now,
                            "tap": t,
                            "beer": curr_beer_name,
                            "oz_poured": round(beer_poured,2) }
    cons_col.insert_one(consumption_record)

    # Update MQTT
    mqtt_publish(t)



# Push data to Home Assistant via MQTT
def mqtt_publish(t):
    # Load MQTT Configuration
    mqtt_query = conf_col.find({"config":"mqtt"},{})
    for m in mqtt_query:
        m_user = m["user"]
        m_pass = m["pass"]
        m_server = m["broker_address"]
        m_port = m["broker_port"]

    # Load Topic Configuration
    topic_query = beer_col.find({"_id":t},{})
    for r in topic_query:
        beer_topic = r["beer_topic"]
        keg_cap_topic = r["keg_cap_topic"]
        keg_rem_topic = r["keg_rem_topic"]
        beers_rem_topic = r["beers_rem_topic"]
        beer_name = r["beer_name"]
        keg_cap = r["keg_oz_capacity"]
        keg_rem = r["keg_oz_remaining"]
        beers_rem = round(keg_rem/12,0)

    # Connect to MQTT Server
    m_client = mqtt.Client("kegerator")
    m_client.username_pw_set(username=m_user,password=m_pass)
    m_client.connect(m_server)

    # Publish Data
    m_client.publish(beer_topic,beer_name)
    m_client.publish(keg_cap_topic,str(keg_cap))
    m_client.publish(keg_rem_topic,str(keg_rem))
    m_client.publish(beers_rem_topic,str(beers_rem))





# Startup LED Routine to indicate system running
def startup_routine():
    t = 0
    while t < 4:
        GPIO.output(t1_led,GPIO.HIGH)
        GPIO.output(t2_led,GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(t1_led,GPIO.LOW)
        GPIO.output(t2_led,GPIO.LOW)
        time.sleep(0.2)
        t += 1



# ========== MAIN ========== #
if __name__ == '__main__':
    # Database Setup
    con = pymongo.MongoClient("mongodb://localhost:27017/") # Connection to MongoDB
    db = con["kegwatch"]            # Database
    beer_col = db["beer"]           # Collection: beer
    conf_col = db["conf"]           # Collection: conf
    cons_col = db["consumption"]    # Collection: consumption

    # Load Initial Configs
    gpio_query = conf_col.find({"config":"hardware"},{})
    for r in gpio_query:
        t1_gpio = r["tap_1_gpio"]
        t2_gpio = r["tap_2_gpio"]
        t1_led = r["tap_1_led"]
        t2_led = r["tap_2_led"]

    # GPIO Setup
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(t1_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(t2_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(t1_led,GPIO.OUT)
    GPIO.setup(t2_led,GPIO.OUT)

    # Run Startup Indication
    startup_routine()

    # Create Event Detection
    GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300) 
    GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300) 

    # Persist Service
    #message = input("")
    while True:
        time.sleep(.001)

    # Cleanup GPIO
    GPIO.cleanup()