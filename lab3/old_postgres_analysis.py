import random
import time
from pg8000.native import Connection

n = 10000

# --- RECORD GENERATOR ---
def generate_record(user_id: int):
    return (
        random.randint(1, 100),
        random.randint(1, 100),
        user_id,
        random.uniform(0, 1000),
        random.choice(["alpha", "beta", "gamma"]),
    )

def main():
    # Connect using native arguments
    conn = Connection(
        user="post",
        password="post",
        host="localhost",
    )

    # Clean slate
    conn.run("DROP TABLE IF EXISTS benchmark")
    conn.run("""
        CREATE TABLE benchmark (
            id SERIAL PRIMARY KEY,
            x_pos INT,
            y_pos INT,
            user_id INT,
            score FLOAT,
            label TEXT
        )
    """)

    print(f"PostgreSQL ({n:,} records) using pg8000")

    # --- CREATE ---
    print("\n--- CREATE ---")
    start = time.perf_counter()
    conn.run(
        "INSERT INTO benchmark (x_pos, y_pos, user_id, score, label) VALUES (:x, :y, :u, :s, :l)",
        x=random.randint(1, 100), y=random.randint(1, 100), u=n + 1, s=1.0, l="alpha"
    )
    print(f"Insert one record: {(time.perf_counter() - start)*1000:.2f} ms")

    records = [generate_record(i) for i in range(n)]

    start = time.perf_counter()
    
    # Create a cursor to handle the batch operation
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO benchmark (x_pos, y_pos, user_id, score, label) VALUES (%s, %s, %s, %s, %s)",
        records
    )
    # Commit the transaction so the data persists
    conn.commit()
    
    print(f"Insert many {n:,}: {(time.perf_counter() - start)*1000:.2f} ms")

    # --- READ ---
    print("\n--- READ ---")
    # pg8000 returns rows directly
    all_rows = conn.run("SELECT * FROM benchmark")
    print(f"\nSelect all {len(all_rows):,} records: {(time.perf_counter() - start)*1000:.2f} ms")

    # Find user 42
    result = conn.run("SELECT * FROM benchmark WHERE user_id = 42")
    print(f"Find user 42: {len(result)} row(s)")

    # --- UPDATE ---
    print("\n--- UPDATE ---")
    # pg8000's run() method returns the number of rows affected
    count = conn.run("UPDATE benchmark SET x_pos = 99 WHERE user_id = 42")
    print(f"Update one user=42: Affected {count} rows")

    # --- DELETE ---
    print("\n--- DELETE ---")
    deleted = conn.run("DELETE FROM benchmark WHERE user_id = 1")
    print(f"Delete one user=1: Deleted {deleted} rows")

    conn.run("DROP TABLE benchmark")
    conn.close()

if __name__ == "__main__":
    main()