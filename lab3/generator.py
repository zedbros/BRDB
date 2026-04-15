import random
import pymongo

# Connect to the local MongoDB (assuming it's running on the default port 27017)
client = pymongo.MongoClient("mongodb://mango:mango@localhost:27017")

# Create or select a database (e.g., "mydb")
db = client["mydb"]

# Create or select a collection (e.g., "mycollection")
collection = db["mycollection"]

# Generate a random number between 1 and 100 (inclusive)
for i in range(10):
	random_x = random.randint(1, 100)
	random_y = random.randint(1, 100)
	random_user = random.randint(1,10)
	
	
	json_document = {
		"x-pos" : random_x,
		"y-pos" : random_y,
		"user" : random_user
	}
	collection.insert_one(json_document)
	print(json_document)	
