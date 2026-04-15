import pymongo

# Connect to the local MongoDB (assuming it's running on the default port 27017)
client = pymongo.MongoClient("mongodb://mango:mango@localhost:27017")

# Create or select a database (e.g., "mydb")
db = client["mydb"]

# Create or select a collection (e.g., "mycollection")
collection = db["mycollection"]


retval = collection.find()
# or if you want something specific:
retval = collection.find({"user":10})

for data in retval: 
	print(data)
