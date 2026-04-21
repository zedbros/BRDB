import random
import time
import pymongo

n = 1000  # number of records to insert into db

client = pymongo.MongoClient("mongodb://mango:mango@localhost:27017")
db = client["mydb"]
collection = db["benchmark"]
collection.drop()


# --- CREATE ---
print(f"MongoDB ({n:,} records)")
print(f"\n--- CREATE ---")
def generate_record(user_id: int) -> dict:
    return {
        "x_pos": random.randint(1, 100),
        "y_pos": random.randint(1, 100),
        "user": user_id,
        "score": random.uniform(0, 1000),
        "label": random.choice(["alpha", "beta", "gamma"]),
    }
records = [generate_record(i) for i in range(n)]

start = time.perf_counter()
collection.insert_one(generate_record(n + 1))
elapsed = time.perf_counter() - start
print(f"Insert one record: {elapsed*1000:.2f} ms")

start = time.perf_counter()
collection.insert_many(records)
elapsed = time.perf_counter() - start
print(f"Insert many {n:,}: {elapsed*1000:.2f} ms")



# --- READ ---
print(f"\n--- READ ---")
start = time.perf_counter()
all_docs = list(collection.find())
elapsed = time.perf_counter() - start
print(f"\nFind all {len(all_docs):,} records: {elapsed*1000:.2f} ms")

# Without index
start = time.perf_counter()
result = list(collection.find({"user": 42}))
elapsed = time.perf_counter() - start
print(f"Find user 42 (no index): {elapsed*1000:.2f} ms  -> {len(result)} doc(s)")

# With index
collection.create_index("user")
start = time.perf_counter()
result = list(collection.find({"user": 42}))
elapsed = time.perf_counter() - start
print(f"Find user 42 (with index): {elapsed*1000:.2f} ms  -> {len(result)} doc(s)")

# Filter by label
start = time.perf_counter()
result = list(collection.find({"label": "alpha"}))
elapsed = time.perf_counter() - start
print(f"Find label 'alpha': {elapsed*1000:.2f} ms  -> {len(result)} doc(s)")



# --- UPDATE ---
print(f"\n--- UPDATE ---")
start = time.perf_counter()
collection.update_one({"user": 42}, {"$set": {"x_pos": 99}})
elapsed = time.perf_counter() - start
print(f"\nUpdate one user=42: {elapsed*1000:.2f} ms")

start = time.perf_counter()
res = collection.update_many({"label": "beta"}, {"$set": {"label": "beta_updated"}})
elapsed = time.perf_counter() - start
print(f"Update many label=beta: {elapsed*1000:.2f} ms  -> {res.modified_count} doc(s)")

# --- DELETE ---
print(f"\n--- DELETE ---")
start = time.perf_counter()
collection.delete_one({"user": 1})
elapsed = time.perf_counter() - start
print(f"\nDelete one user=1: {elapsed*1000:.2f} ms")

start = time.perf_counter()
res = collection.delete_many({"label": "gamma"})
elapsed = time.perf_counter() - start
print(f"Delete many label=gamma: {elapsed*1000:.2f} ms  -> {res.deleted_count} doc(s)")

start = time.perf_counter()
collection.drop()
elapsed = time.perf_counter() - start
print(f"Drop collection: {elapsed*1000:.2f} ms")

print("--- --- FINISHED MONGODB --- ---\n")
client.close()
