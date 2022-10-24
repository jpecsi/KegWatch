#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import time, os
from datetime import datetime
from datetime import date
import paho.mqtt.client as mqtt
from threading import Thread
import configparser
import mysql.connector
import random


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


def gen_data():
    tap_idx = [1,2]
    time_idx = [1,2,3]

    selected_tap = random.choice(tap_idx)
    selected_time = random.choice(time_idx)

    if selected_tap == 1:
        print("[TAP 1] Tap open for " + str(selected_time) + " seconds")
        tap1(1)
        time.sleep(selected_time)
        tap1(0)
        print("[TAP 1] Tap closed")
    if selected_tap == 2:
        print("[TAP 2] Tap open for " + str(selected_time) + " seconds")
        tap2(1)
        time.sleep(selected_time)
        tap2(0)
        print("[TAP 2] Tap closed")



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
def tap1(s):
    # Setup Variables
    global t1_start
    global t1_end

    # If tap opens, start the timer...
    if s == 1:  
        t1_start = time.perf_counter()      # Start the timer
      
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if s == 0:
        t1_end = time.perf_counter()        # Stop the timer
        calc_beer(1,(t1_end - t1_start))    # Calculate the remaining beer
        
        

# Tap 2 Handler
def tap2(s):
    # Setup variables
    global t2_start
    global t2_end

    # If tap opens, start the timer...
    if s == 1:
        t2_start = time.perf_counter()      # Start the timer
        
    
    # If tap closes, stop the timer and calculate the remaining beer!
    if s == 0:
        t2_end = time.perf_counter()        # Stop the timer
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

        if beer_poured > 32:
            pass
        else:
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

        



# ========== MAIN ========== #
if __name__ == '__main__':
    # Set working directory
    cf_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config'))
    cf = cf_path + "/settings.conf"

    # Read config and beer files
    config = configparser.ConfigParser()
    config.read(cf)

    while True:
        global cuser
        try:
            cuser = input("ENTER NAME: ")
        except KeyboardInterrupt:
            print()
            exit()

        # Catch game-mode barcodes
        if cuser[0] == '0':
            if config.getboolean("game_mode", "enabled"):
                game_logic(cuser[1:],"Mixed Drink",8,config.getfloat("game_mode","average_abv"))
        else:
            gen_data()