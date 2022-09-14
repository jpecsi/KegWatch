# ========== LIBRARIES ========== #
import pymongo
import time
import RPi.GPIO as GPIO 
import configparser



# ========== FUNCTIONS ========== #
# Tap 1 Handler
def tap1(channel):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t1_start = time.perf_counter()
        GPIO.output(t1_led,GPIO.LOW)
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t1_end = time.perf_counter()
        GPIO.output(t1_led,GPIO.HIGH)

        # Calculate flow rate
        ttp = t1_end-t1_start
        flow = int(oz)/ttp
        print("[RESULT] It took " + str(ttp) + " seconds to pour " + str(oz) + " oz. Flow rate is " + str(flow) + " oz/sec")

        # Update config
        config.set('tap_1', 'flow_rate', str(flow))
        with open('settings.conf', 'w') as configfile:
            config.write(configfile)

        # Exit
        print("\nCalibration Complete!")
        GPIO.output(t1_led,GPIO.LOW)
        exit()


# Tap 2 Handler
def tap2(channel):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if GPIO.input(channel) == 1:
        t2_start = time.perf_counter()
        GPIO.output(t2_led,GPIO.LOW)

    # If tap closes, stop the timer and calculate the remaining beer!
    if GPIO.input(channel) == 0:
        t2_end = time.perf_counter()
        GPIO.output(t2_led,GPIO.HIGH)

        # Calculate flow rate
        ttp = t2_end-t2_start
        flow = int(oz)/ttp
        print("[RESULT] It took " + str(ttp) + " seconds to pour " + str(oz) + " oz. Flow rate is " + str(flow) + " oz/sec")

        # Update config
        config.set('tap_2', 'flow_rate', str(flow))
        with open('settings.conf', 'w') as configfile:
            config.write(configfile)

        # Exit
        print("\nCalibration Complete! Exiting...")
        GPIO.output(t2_led,GPIO.LOW)
        exit()
        



# ========== MAIN ========== #
if __name__ == '__main__':

    # ===== LOAD CONFIGURATION ===== #
    # Read config and beer files
    config = configparser.ConfigParser()
    config.read('settings.conf')
    
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


    # Present Menu
    print("\nKegWatch Calibration\n====================\n")
    selected_tap = input("Which tap will be used to calibrate (1/2)? ")
    oz = input("How many oz are you pouring? ")
    
    # Create Event Detection
    if selected_tap == "1":
        GPIO.add_event_detect(t1_gpio, GPIO.BOTH, callback=tap1,bouncetime=300) 
        GPIO.output(t1_led,GPIO.HIGH)
    if selected_tap == "2":
        GPIO.add_event_detect(t2_gpio, GPIO.BOTH, callback=tap2,bouncetime=300)
        GPIO.output(t2_led,GPIO.HIGH)

    print("\nBegin pouring!")
    run = input() 

    # Cleanup GPIO
    GPIO.cleanup()
