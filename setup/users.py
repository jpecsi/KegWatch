#!/usr/bin/env python3

# ========== LIBRARIES ========== #
import configparser
import mysql.connector
from datetime import datetime
from prettytable import PrettyTable





# ========== FUNCTIONS ========== #
def present_menu():
    print("\n[KegWatch User Management]\n==========================")
    print("(1) List Users")
    print("(2) Add User")
    print("(3) Delete User")
    print("(4) Modify User")
    print("(5) Register Cup to User")
    print("(6) Exit")
    print()


    return(input("Menu Selection: "))


def list_users():
    print("CURRENT USERS")
    user_tbl = PrettyTable(['ID', 'First Name', 'Last Name'])
    db.execute("SELECT * FROM consumers")
    for user in db:
        user_tbl.add_row([user[0], user[1], user[2]])

    print(user_tbl)


def add_user():
    print("NEW USER")
    fname = input("First Name: ")
    lname = input("Last Name: ")

    valid = 0
    while valid == 0:
        print("\nYou Entered: " + fname + " " + lname)
        if (input("Confirm New User (y/n)? ")) == "y":
            query = ("INSERT INTO consumers (first_name,last_name) VALUES (%s,%s)")
            db.execute(query,(fname,lname))
            db_server.commit()
            valid = 1
    print("\n")
    list_users()

def delete_user():
    list_users()
    choice = input("Enter user ID to be deleted: ")
    query = ("SELECT * FROM consumers WHERE id=%s")
  
    db.execute(query,(choice,))

    user_tbl = PrettyTable(['ID', 'First Name', 'Last Name'])
    for user in db:
        user_tbl.add_row([user[0], user[1], user[2]])
    print(user_tbl)
    confirm = input("Confirm deleting this user (y/n)? ")
    if confirm == "y":
        del_query = ("DELETE FROM consumers WHERE id=%s")
        db.execute(del_query,(choice,))
        print("User Deleted!")

def modify_user():
    list_users()
    choice = input("Enter user ID to be modified: ")
    query = ("SELECT * FROM consumers WHERE id=%s")
  
    db.execute(query,(choice,))

    user_tbl = PrettyTable(['ID', 'First Name', 'Last Name'])
    for user in db:
        user_tbl.add_row([user[0], user[1], user[2]])
    print(user_tbl)

    print("\nMODIFY USER")
    fname = input("First Name: ")
    lname = input("Last Name: ")

    valid = 0
    while valid == 0:
        print("\nYou Entered: " + fname + " " + lname)
        if (input("Confirm modification (y/n)? ")) == "y":
            query = ("UPDATE consumers SET first_name=%s,last_name=%s WHERE id=%s")
            db.execute(query,(fname,lname,choice,))
            db_server.commit()
            valid = 1
    print("\n")
    list_users()


def register_cup():
    user_tbl = PrettyTable(['ID', 'First Name', 'Last Name', 'Assigned Cup'])
    db.execute("SELECT * FROM consumers")
    users,cups = [],[]
    for user in db:
        users.append(user)

    for u in users:
        cup_query = ("SELECT id FROM cup_inventory WHERE user_id=%s")
        db.execute(cup_query,(u[0],))
        c_id = "None"
        for c in db:
            c_id = c[0]

        user_tbl.add_row([u[0],u[1],u[2],c_id])
    print(user_tbl)

    valid = 0
    while valid == 0:
        u_mod = input("Enter user ID to be modified: ")
        c_mod = input("Enter cup ID to assign: ")
        selected_user = ""
        query = ("SELECT * FROM consumers WHERE id=%s")
        db.execute(query,(u_mod,))
        for s_u in db:
            selected_user = (s_u[1] + " " + s_u[2])


        print("\nYou would like to assign cup [" + c_mod + "] to " + selected_user)
        if (input("Confirm modification (y/n)? ")) == "y":
            assign_query = ("INSERT INTO cup_inventory (id,user_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE id=%s,user_id=%s")
            db.execute(assign_query,(c_mod,u_mod,c_mod,u_mod,))
            db_server.commit()
            valid = 1
    print("\n")

# ========== MAIN ========== #
if __name__ == '__main__':

    # ===== LOAD CONFIGURATION ===== #
    # Read config and beer files
    config = configparser.ConfigParser()
    config.read('settings.conf')

    # === DATABASE === #
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
                delete_user()
            elif action == "4":
                modify_user()
            elif action == "5":
                register_cup()
            elif action == "6":
                exit()
            else:
                print("Invalid menu selection. Try again!\n")
    except KeyboardInterrupt:
        print("")
        exit()