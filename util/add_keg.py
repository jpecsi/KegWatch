#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import configparser, os
import datetime
import uuid
from prettytable import PrettyTable
import mysql.connector
from datetime import datetime
from datetime import date


# ========== FUNCTIONS ========== #
def colorize(c,t):
    colors = {
        "PURPLE": '\033[95m',
        "BLUE": '\033[94m',
        "CYAN": '\033[96m',
        "GREEN": '\033[92m',
        "YELLOW": '\033[93m',
        "RED": '\033[91m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m'
    }

    if c not in colors:
        return t
    else:
        return (colors[c] + str(t) + '\033[0m')



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



# Read from the database
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
        '1': 0,
        '2': 0
    }

    # Keg sizes
    kegs = {
        '1/6': 661,
        '1/4': 992,
        '1/2': 1984
    }

    # Run (loop)
    try:
        run = 1
        while run == 1:
            # Display current beers on tap
            print(colorize("BOLD","\nKegWatch Keg Manager"))
            
            keg_data = read_db("SELECT name,tap,abv,capacity,remaining,status FROM keg_log WHERE status=%s ORDER BY tap ASC",(1,))
            keg_tbl = PrettyTable(['Tap', 'Beer', 'ABV', 'Capacity', 'Remaining'])
            if len(keg_data) == 0:
                print(colorize("RED", "No Active Beers!"))
            else:
                print(colorize("PURPLE", "\nActive Kegs"))
                for keg in keg_data:
                    keg_tbl.add_row([keg[1],keg[0],keg[2],keg[3],keg[4]])
                    taps.update({str(keg[1]): keg[5]})
                print(keg_tbl)

            # Get input & validate the tap to modify
            validate = 0
            while validate == 0:
                tap_input = input("\nWhich tap would you like to add the keg to? ")
                if tap_input not in taps:
                    print(colorize("YELLOW", "Invalid tap!"))
                if int(taps[tap_input]) == 1:
                    print(colorize("YELLOW","Tap Already Active!"))
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

            # Get the ABV
            abv = input("What is the ABV of the beer? ")
            abv = float(abv)

            # Display user's input and confirm change
            print("\n\n[TAP " + tap_input + "] " + keg_input + " keg of " + beer_name + "(" + str(abv) + "%)")
            confirm = input("Confirm Changes (y/n)? ")

            # Input confirmed...
            if confirm == "y":
                # Current date (properly formatted)
                now = '{dt.year}-{dt.month}-{dt.day}'.format(dt = datetime.now())

                # Generate UUID for keg
                keg_id = str(uuid.uuid4())

                # Add the keg
                write_to_db("INSERT INTO keg_log (id,name,tap,abv,capacity,remaining,date_tapped,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(keg_id,beer_name,int(tap_input),abv,kegs[keg_input],kegs[keg_input],now,1))
                
                # See if the user needs to add another keg, otherwise exit
                run_again = input("\nAdd anohter keg (y/n)? ")
                if run_again == "y":
                    run = 1
                else:
                    run = 0
    except KeyboardInterrupt:
        print("\n[" + str(datetime.now()) + "] EXITING")
        exit()
        