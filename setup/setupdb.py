import pymongo
import json

# ========== FUNCTIONS ========== #

# Check for Collections
def validate_db(d):
    try:
        d.validate_collection("beer")
    except pymongo.errors.OperationFailure:
        print("Beer Collection Does Not Exist | Creating Now")
        create_beer(d)

    try:
        d.validate_collection("conf")
    except pymongo.errors.OperationFailure:
        print("Conf Collection Does Not Exist | Creating Now")
        create_conf(d)


# Create Beer Collection
def create_beer(d):
    with open('beer.json') as beer_file:
        beer_data = json.load(beer_file)
    d["beer"].insert_many(beer_data)


# Create Conf Collection
def create_conf(d):
    with open('conf.json') as conf_file:
        conf_data = json.load(conf_file)
    d["conf"].insert_many(conf_data)





# ========== MAIN ========== #
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["kegwatch"]
validate_db(db)

