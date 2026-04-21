import random
import time
import asyncio
import asyncpg

n = 10000  # number of records


# --- RECORD GENERATOR ---
def generate_record(user_id: int):
    return (
        random.randint(1, 100),          # x_pos
        random.randint(1, 100),          # y_pos
        user_id,                         # user_id
        random.uniform(0, 1000),         # score
        random.choice(["alpha", "beta", "gamma"]),  # label
    )


async def main():
    conn = await asyncpg.connect(
        user="post",
        password="post",
        port=5432,
        host="localhost"
    )

    # Clean slate
    await conn.execute("DROP TABLE IF EXISTS benchmark")

    await conn.execute("""
        CREATE TABLE benchmark (
            id SERIAL PRIMARY KEY,
            x_pos INT,
            y_pos INT,
            user_id INT,
            score FLOAT,
            label TEXT
        )
    """)

    print(f"PostgreSQL ({n:,} records)")

    # --- CREATE ---
    print("\n--- CREATE ---")

    start = time.perf_counter()
    await conn.execute(
        "INSERT INTO benchmark (x_pos, y_pos, user_id, score, label) VALUES ($1,$2,$3,$4,$5)",
        *generate_record(n + 1)
    )
    elapsed = time.perf_counter() - start
    print(f"Insert one record: {elapsed*1000:.2f} ms")

    records = [generate_record(i) for i in range(n)]

    start = time.perf_counter()
    await conn.executemany(
        "INSERT INTO benchmark (x_pos, y_pos, user_id, score, label) VALUES ($1,$2,$3,$4,$5)",
        records
    )
    elapsed = time.perf_counter() - start
    print(f"Insert many {n:,}: {elapsed*1000:.2f} ms")

    # --- READ ---
    print("\n--- READ ---")

    start = time.perf_counter()
    all_rows = await conn.fetch("SELECT * FROM benchmark")
    elapsed = time.perf_counter() - start
    print(f"Select all {len(all_rows):,} records: {elapsed*1000:.2f} ms")

    # Without index
    start = time.perf_counter()
    result = await conn.fetch("SELECT * FROM benchmark WHERE user_id = 42")
    elapsed = time.perf_counter() - start
    print(f"Find user 42 (no index): {elapsed*1000:.2f} ms  -> {len(result)} row(s)")

    # With index
    await conn.execute("CREATE INDEX idx_user_id ON benchmark(user_id)")

    start = time.perf_counter()
    result = await conn.fetch("SELECT * FROM benchmark WHERE user_id = 42")
    elapsed = time.perf_counter() - start
    print(f"Find user 42 (with index): {elapsed*1000:.2f} ms  -> {len(result)} row(s)")

    # Filter by label
    start = time.perf_counter()
    result = await conn.fetch("SELECT * FROM benchmark WHERE label = 'alpha'")
    elapsed = time.perf_counter() - start
    print(f"Find label 'alpha': {elapsed*1000:.2f} ms  -> {len(result)} row(s)")

    # --- UPDATE ---
    print("\n--- UPDATE ---")
    start = time.perf_counter()
    await conn.execute(
        "UPDATE benchmark SET x_pos = 99 WHERE user_id = 42"
    )
    elapsed = time.perf_counter() - start
    print(f"Update one user=42: {elapsed*1000:.2f} ms")

    start = time.perf_counter()
    result = await conn.execute(
        "UPDATE benchmark SET label = 'beta_updated' WHERE label = 'beta'"
    )
    elapsed = time.perf_counter() - start

    # result looks like "UPDATE <count>"
    updated_count = int(result.split()[-1])
    print(f"Update many label=beta: {elapsed*1000:.2f} ms  -> {updated_count} row(s)")

    # --- DELETE ---
    print("\n--- DELETE ---")

    start = time.perf_counter()
    await conn.execute("DELETE FROM benchmark WHERE user_id = 1")
    elapsed = time.perf_counter() - start
    print(f"nDelete one user=1: {elapsed*1000:.2f} ms")

    start = time.perf_counter()
    result = await conn.execute("DELETE FROM benchmark WHERE label = 'gamma'")
    elapsed = time.perf_counter() - start

    deleted_count = int(result.split()[-1])
    print(f"Delete many label=gamma: {elapsed*1000:.2f} ms  -> {deleted_count} row(s)")

    start = time.perf_counter()
    await conn.execute("DROP TABLE benchmark")
    elapsed = time.perf_counter() - start
    print(f"Drop table: {elapsed*1000:.2f} ms")

    print("--- --- FINISHED POSTGRESQL --- ---\n")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())