import random
import time
import json
import redis

n = 10000

# Redis is a key-value store: no "tables" or "collections".
# Strategy: store each record as a JSON string at key "record:<user_id>"
# and maintain a set "all_records" for bulk scans.
r = redis.Redis(host="localhost", port=6379, decode_responses=True, password="red")
r.flushdb()


# --- CREATE ---
print(f"Redis Benchmark ({n:,} records)")
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

# Insert 1
single = generate_record(n + 1)
start = time.perf_counter()
r.set(f"record:{single['user']}", json.dumps(single))
r.sadd("all_records", f"record:{single['user']}")
r.sadd(f"label:{single['label']}", f"record:{single['user']}")
elapsed = time.perf_counter() - start
print(f"Set 1 record: {elapsed*1000:.2f} ms")

# Insert many
start = time.perf_counter()
pipe = r.pipeline()
for rec in records:
    key = f"record:{rec['user']}"
    pipe.set(key, json.dumps(rec))
    pipe.sadd("all_records", key)
    # Secondary index by label (set per label)
    pipe.sadd(f"label:{rec['label']}", key)
pipe.execute()
elapsed = time.perf_counter() - start
print(f"\nPipeline set {n:,} records: {elapsed*1000:.2f} ms")



# --- READ ---
# Read all
start = time.perf_counter()
all_keys = r.smembers("all_records")
pipe = r.pipeline()
for key in all_keys:
    pipe.get(key)
all_values = pipe.execute()
elapsed = time.perf_counter() - start
print(f"\nGet all {len(all_values):,} records: {elapsed*1000:.2f} ms")

# Read single by key O(1)
start = time.perf_counter()
val = r.get("record:42")
result = json.loads(val) if val else None
elapsed = time.perf_counter() - start
print(f"Get record=42 (direct key): {elapsed*1000:.2f} ms  -> {'found' if result else 'not found'}")

# Read by label
start = time.perf_counter()
label_keys = r.smembers("label:alpha")
pipe = r.pipeline()
for key in label_keys:
    pipe.get(key)
label_results = pipe.execute()
elapsed = time.perf_counter() - start
print(f"Get label='alpha' (index set): {elapsed*1000:.2f} ms  -> {len(label_results)} doc(s)")






# --- UPDATE ---
# Update one record
start = time.perf_counter()
raw = r.get("record:42")
if raw:
    rec = json.loads(raw)
    rec["x_pos"] = 99
    r.set("record:42", json.dumps(rec))
elapsed = time.perf_counter() - start
print(f"\nUpdate record=42: {elapsed*1000:.2f} ms")

# Rename all "beta", "beta_updated"
start = time.perf_counter()
beta_keys = r.smembers("label:beta")
pipe = r.pipeline()
count = 0
for key in beta_keys:
    raw = r.get(key)
    if raw:
        rec = json.loads(raw)
        rec["label"] = "beta_updated"
        pipe.set(key, json.dumps(rec))
        pipe.sadd("label:beta_updated", key)
        count += 1
pipe.srem("label:beta", *beta_keys) if beta_keys else None
pipe.execute()
elapsed = time.perf_counter() - start
print(f"Update many label=beta: {elapsed*1000:.2f} ms  -> {count} record(s)")





# --- DELETE ---
# Delete one
start = time.perf_counter()
r.delete("record:1")
r.srem("all_records", "record:1")
elapsed = time.perf_counter() - start
print(f"\nDelete record=1 : {elapsed*1000:.2f} ms")

# Delete many (gamma)
start = time.perf_counter()
gamma_keys = r.smembers("label:gamma")
if gamma_keys:
    pipe = r.pipeline()
    pipe.delete(*gamma_keys)
    pipe.srem("all_records", *gamma_keys)
    pipe.delete("label:gamma")
    pipe.execute()
elapsed = time.perf_counter() - start
print(f"Delete label=gamma: {elapsed*1000:.2f} ms  -> {len(gamma_keys)} record(s)")

# Flush all
start = time.perf_counter()
r.flushdb()
elapsed = time.perf_counter() - start
print(f"flushdb (drop): {elapsed*1000:.2f} ms")

print("--- --- FINISHED REDIS --- ---\n")
r.close()
