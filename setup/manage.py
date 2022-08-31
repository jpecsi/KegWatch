# ========== LIBRARIES ========== #
import pymongo
from datetime import datetime





# ========== FUNCTIONS ========== #
# Display current configuration for all active taps
def show_settings(t):
    beer_settings = beer_col.find({"_id":int(t)},{})
    for b in beer_settings:
        print("\n=============================")
        print("[TAP " + str(t) + " CURRENT CONFIGURATION]")
        print("=============================")
        print("Beer: " + b['beer_name'])
        print("Keg Capacity: " + str(b['keg_oz_capacity']) + "oz")
        print("Keg Remaining: " + str(b['keg_oz_remaining']) + "oz")
        print("Date Tapped: " + str(b['date_tapped']))
        print("Last Poured: " + str(b['last_pour']) + "\n")


# Update the tap settings
def modify_tap(t):
    # Display the menu
    action = input("(R)emove or (C)hange Beer on Tap " + str(t) + "? ")

    # Remove the beer after double checking with the user
    if action == "R":
        double_check = input("Are you sure you want to remove the beer from Tap " + str(t) + " (y/n)? ")
        if double_check == "y":
            beer_col.update_one({"_id":t},{"$set":{"active":0}})
            beer_name = ""
            capacity = 0
            active = 0
            now = ""
            
            print("Beer Removed!")
        else:
            print("Glad I Checked!")

    # Modify/add the new beer settings
    if action == "C":
        run_menu = 1
        while run_menu == 1:
            # Get user input for new settings
            print("\n[TAP " + str(t) + " MODIFICATION]")
            beer_name = input("Beer Name: ")
            keg_size = input("Keg Size [1/4 or 1/6]: ")
            
            # Show new settings
            print("\n[Configuration Review]")
            print("Tap: " + str(t))
            print("Beer: " + beer_name)
            print("Keg Size: " + keg_size)

            # Ask user to approve changes
            validate = input("\nConfirm (y/n)? ")

            # Input Validation
            if validate == "y":
                active = 1
                now = datetime.now()
                if keg_size == "1/4":
                    capacity = 992
                    run_menu = 0
                elif keg_size == "1/6":
                    capacity = 672
                    run_menu = 0
                else:
                    print("Invalid Keg Size. Try Again!")

    # Update Database
    beer_col.update_one({"_id":t},{"$set":{"beer_name":beer_name}})     
    beer_col.update_one({"_id":t},{"$set":{"keg_oz_capacity":capacity}})
    beer_col.update_one({"_id":t},{"$set":{"keg_oz_remaining":capacity}})
    beer_col.update_one({"_id":t},{"$set":{"date_tapped":now}})
    beer_col.update_one({"_id":t},{"$set":{"last_pour":""}})
    beer_col.update_one({"_id":t},{"$set":{"active":active}})
    
    # Display the new db record
    show_settings(t)



# ========== MAIN ========== #
if __name__ == '__main__':
    # Database Setup
    con = pymongo.MongoClient("mongodb://localhost:27017/") # Connection to MongoDB
    db = con["kegwatch"]        # Database
    beer_col = db["beer"]       # Collection: beer
    conf_col = db["conf"]       # Collection: conf
    

    # Check for Active Beers
    active_beers = beer_col.find({"active":1},{"_id":1})
    for a in active_beers:
        show_settings(a['_id'])

    
    # Present Menu
    safe = 0
    while safe == 0:
        selected_tap = input("Which tap (1|2) would you like to modify? ")
        if selected_tap == "1" or selected_tap == "2":
            safe = 1
            modify_tap(int(selected_tap))
        else:
            print("Invalid Selection. Try Again!")

    # End of script...bye
    print("\nExiting!\n")