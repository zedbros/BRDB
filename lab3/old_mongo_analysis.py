import random
import pymongo

# Connect to the local MongoDB (assuming it's running on the default port 27017)
client = pymongo.MongoClient("mongodb://mango:mango@localhost:27017")
# Create or select a database (e.g., "mydb")
db = client["mydb"]
# Create or select a collection (e.g., "mycollection")
collection = db["mycollection"]

# --- WRITER (Create) ---
# Generate a random number between 1 and 100 (inclusive)
for i in range(10):
	random_x = random.randint(1,100)
	random_y = random.randint(1,100)
	# random_user = random.randint(1,10)
	random_user = i
	
	json_document = {
		"x-pos" : random_x,
		"y-pos" : random_y,
		"user" : random_user
	}
	collection.insert_one(json_document)
	# print(json_document)

# --- READER (Read) ---
retval = collection.find()
# or if you want something specific:
retval = collection.find({"user":10})

# print("--- SIMPLE PRINT FUNCTION ---")
# for data in retval: 
# 	print(data)

# --- UPDATE --- 
print("All unpair numbered users will have 100 added to their x.")
for i in collection.find():
	if(i['user'] % 2 != 0):
		collection.find_one_and_update({'id': i['user']},{'$set': {"x-pos" : 69}})


# --- DELETE --- 
# one
print("GOING TO REMOVE user with the number == 1")
collection.delete_one({'user': 1})

# many
# collection.delete_many()

print("REMOVED specific one(s) ?")
for data in collection.find(): 
	print(data)

# all
collection.drop()
