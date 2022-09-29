#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import configparser, os
import datetime


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
        '1': "tap_1",
        '2': "tap_2"
    }

    # Keg sizes
    kegs = {
        '1/6': 661,
        '1/4': 992,
        '1/2': 1984
    }

    # Run (loop)
    run = 1
    while run == 1:
        # Display current beers on tap
        print("\nKegWatch Keg Manager\n====================")
        for tapid in taps:
            print("[TAP " + str(tapid) + "] " + config[taps[tapid]]["beer_name"])

        # Get input & validate the tap to modify
        validate = 0
        while validate == 0:
            tap_input = input("\nWhich tap would you like to add the keg to? ")
            if tap_input not in taps:
                print("Invalid tap!")
            else:
                validate = 1

        # Get input & validate the keg size
        validate = 0
        while validate == 0:
            keg_input = input("What size is the keg (1/4 or 1/6)? ")
            if keg_input not in kegs:
                print("Invalid keg size!")
            else:
                validate = 1

        # Get the beer name
        beer_name = input("What is the name of the beer? ")

        # Display user's input and confirm change
        print("\n\n[TAP " + tap_input + "] " + keg_input + " keg of " + beer_name)
        confirm = input("Confirm Changes (y/n)? ")

        # Input confirmed...
        if confirm == "y":
            # Current date (properly formatted)
            now = '{dt.year}-{dt.month}-{dt.day}'.format(dt = datetime.datetime.now())

            # Update settings.conf
            config.set(taps[tap_input], 'beer_name', beer_name)
            config.set(taps[tap_input],'keg_capacity',str(kegs[keg_input]))
            config.set(taps[tap_input],'keg_remaining',str(kegs[keg_input]))
            config.set(taps[tap_input],'date_tapped',str(now))
            with open(cf, 'w') as configfile:
                config.write(configfile)
            
            # See if the user needs to add another keg, otherwise exit
            run_again = input("\nAdd anohter keg (y/n)? ")
            if run_again == "y":
                run = 1
            else:
                run = 0

        