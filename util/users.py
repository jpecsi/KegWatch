#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import configparser
import mysql.connector
from datetime import datetime
from prettytable import PrettyTable
import os





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



def present_menu():
    print("\n" + colorize("UNDERLINE",(colorize("BOLD", "KegWatch User Management"))) + "\n")
    
    print(colorize("GREEN", "(1) List Users"))
    print(colorize("GREEN", "(2) Add User"))
    print(colorize("YELLOW", "(3) Modify User"))
    print(colorize("YELLOW", "(4) Delete User"))
    print(colorize("RED", "(5) Exit"))
    print()

    return(input("Menu Selection: "))



def list_users():
    print(colorize("BOLD","\nRegistered Users"))
    user_tbl = PrettyTable([colorize("BOLD",colorize("PURPLE",'Name')), colorize("BOLD",colorize("PURPLE",'Body Category'))])
    user_tbl.align[colorize("BOLD",colorize("PURPLE",'Name'))] = "l"
    db_data = read_db("SELECT * FROM consumers", None)
   
    for user in db_data:
        user_tbl.add_row([colorize("PURPLE",user[0]), user[1]])

    
    print(user_tbl)



def add_user():
    print("\n" + colorize("UNDERLINE",(colorize("BOLD", "New User Registration"))) + "\n")
    uname = input("Enter/Scan New User's Name: ")
    bodycat = input("Enter Body Category [0] (petite), [1] (average), [2] (large): ")
    
    valid = 0
    while valid == 0:
        print("\nYou Entered: " + uname + " (Body Type: " + bodycat + ")")
        if (input("Confirm New User (y/n)? ")) == "y":
            write_to_db("INSERT INTO consumers (id,body_cat) VALUES (%s,%s)",((uname,int(bodycat))))
            valid = 1
    print("\n")
    list_users()


def delete_user():
    list_users()
    choice = input("Enter user name to be deleted: ")
    db_data = read_db("SELECT * FROM consumers WHERE id=%s", (choice,))

    user_tbl = PrettyTable([colorize("BOLD",colorize("PURPLE",'Name')), colorize("BOLD",colorize("PURPLE",'Body Category'))])
    user_tbl.align[colorize("BOLD",colorize("PURPLE",'Name'))] = "l"
    for user in db_data:
        user_tbl.add_row([colorize("PURPLE",user[0]), user[1]])
    print(user_tbl)
    confirm = input("Confirm deleting this user (y/n)? ")
    if confirm == "y":
        write_to_db("DELETE FROM consumers WHERE id=%s",(choice,))
    
        


def modify_user():
    list_users()
    choice = input("Enter user ID to be modified: ")
    db_data = read_db("SELECT * FROM consumers WHERE id=%s", (choice,))

    user_tbl = PrettyTable([colorize("BOLD",colorize("PURPLE",'Name')), colorize("BOLD",colorize("PURPLE",'Body Category'))])
    user_tbl.align[colorize("BOLD",colorize("PURPLE",'Name'))] = "l"
    for user in db_data:
        user_tbl.add_row([colorize("PURPLE",user[0]), user[1]])
    print(user_tbl)

    bodycat = input("Enter Body Category [0] (petite), [1] (average), [2] (large): ")

    valid = 0
    while valid == 0:
        print("\nYou Entered: " + uname + (" (Body Category: " + bodycat))
        if (input("Confirm modification (y/n)? ")) == "y":
            write_to_db("UPDATE consumers SET body_cat=%s WHERE id=%s", (bodycat,uname))
            valid = 1
    print("\n")
    list_users()




# ========== MAIN ========== #
if __name__ == '__main__':

    # Set working directory
    cf_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config'))
    cf = cf_path + "/settings.conf"

    # ===== LOAD CONFIGURATION ===== #
    # Read config and beer files
    config = configparser.ConfigParser()
    config.read(cf)

    # === DATABASE === #
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

    # Keep the app going
    try:
        run = 1
        while run == 1:
            action = present_menu()
            if action == "1":
                list_users()
            elif action == "2":
                add_user()
            elif action == "3":
                modify_user()
            elif action == "4":
                delete_user()
            elif action == "5":
                exit()
            else:
                print("Invalid menu selection. Try again!\n")
    except KeyboardInterrupt:
        print("[" + str(datetime.now()) + "] EXITING")
        exit()