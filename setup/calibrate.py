# ========== LIBRARIES ========== #
import pymongo
import time
import RPi.GPIO as GPIO 




# ========== FUNCTIONS ========== #
# Tap 1 Handler
def tap1(channel):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t1_start = time.perf_counter()
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t1_end = time.perf_counter()
        
        # Calculate flow rate
        ttp = t1_end-t1_start
        flow = int(oz)/ttp
        print("[RESULT] It took " + str(ttp) + " seconds to pour " + str(oz) + " oz. Flow rate is " + str(flow) + " oz/sec")

        # Update database
        update_conf = conf_col.update_one({"config":"hardware"},{"$set":{"oz_per_second":flow}})

        print("\nCalibration Complete! Exiting...")
        exit()


# Tap 2 Handler
def tap2(channel):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t2_start = time.perf_counter()
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t2_end = time.perf_counter()

        # Calculate flow rate
        ttp = t2_end-t2_start
        flow = int(oz)/ttp
        print("[RESULT] It took " + str(ttp) + " seconds to pour " + str(oz) + " oz. Flow rate is " + str(flow) + " oz/sec")

        # Update database
        update_conf = conf_col.update_one({"config":"hardware"},{"$set":{"oz_per_second":flow}})

        print("\nCalibration Complete! Exiting...")
        exit()



# ========== MAIN ========== #
if __name__ == '__main__':
    # Database Setup
    con = pymongo.MongoClient("mongodb://localhost:27017/") # Connection to MongoDB
    db = con["kegwatch"]        # Database
    beer_col = db["beer"]       # Collection: beer
    conf_col = db["conf"]       # Collection: conf

    # Load Initial Configs
    gpio_query = conf_col.find({"config":"hardware"},{})
    for r in gpio_query:
        t1_gpio = r["tap_1_gpio"]
        t2_gpio = r["tap_2_gpio"]

    # GPIO Setup
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(t1_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(t2_gpio,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    # Present Menu
    print("\nKegWatch Calibration\n====================\n")
    selected_tap = input("Which tap will be used to calibrate (1/2)? ")
    oz = input("How many oz are you pouring? ")
    
    # Create Event Detection
    if selected_tap == "1":
        GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300) 
    if selected_tap == "2":
        GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300)


    print("\nBegin pouring!")

    run = input() 

    # Cleanup GPIO
    GPIO.cleanup()
