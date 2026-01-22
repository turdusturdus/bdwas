import os
import random
import string
import time
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple

import psycopg2
import mysql.connector
from pymongo import MongoClient, ASCENDING, DESCENDING


SIZES = [1, 100, 2000, 4000, 8000, 20000]
REPEATS = 10
DBNAME = "football_app"

POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://user:password@localhost:5432/football_app")
MYSQL_URI = os.getenv("MYSQL_URI", "mysql://user:password@localhost:3306/football_app")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "football_app")

# --- helpers ---
def now() -> float:
    return time.perf_counter()

def rand_name(i: int) -> str:
    return f"Team_{i:06d}"

def payload_str(kb: int = 1) -> str:
    # ~kb kilobytes payload
    return "".join(random.choices(string.ascii_letters + string.digits, k=kb * 1024))

@dataclass
class ResultRow:
    db: str
    scenario: str
    n: int
    repeat: int
    op: str
    ms: float

def parse_mysql_uri(uri: str) -> Dict[str, str]:
    # very small parser for mysql://user:password@host:3306/db
    assert uri.startswith("mysql://")
    rest = uri[len("mysql://"):]
    creds, hostpart = rest.split("@", 1)
    user, password = creds.split(":", 1)
    hostport, db = hostpart.split("/", 1)
    if ":" in hostport:
        host, port = hostport.split(":", 1)
    else:
        host, port = hostport, "3306"
    return {"user": user, "password": password, "host": host, "port": int(port), "database": db}

# =========================
# Postgres
# =========================
PG_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS bench_items (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  league_id INT NOT NULL,
  founded_year INT NOT NULL,
  payload TEXT NOT NULL
);
"""

PG_DROP = "DROP TABLE IF EXISTS bench_items;"

PG_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_bench_name ON bench_items(name);",
    "CREATE INDEX IF NOT EXISTS idx_bench_league_year ON bench_items(league_id, founded_year);",
]
PG_DROP_INDEXES = [
    "DROP INDEX IF EXISTS idx_bench_name;",
    "DROP INDEX IF EXISTS idx_bench_league_year;",
]

def pg_connect():
    return psycopg2.connect(POSTGRES_DSN)

def pg_setup(conn, with_indexes: bool):
    with conn.cursor() as cur:
        cur.execute(PG_DROP)
        cur.execute(PG_TABLE_DDL)
        if with_indexes:
            for q in PG_CREATE_INDEXES:
                cur.execute(q)
        conn.commit()

def pg_clear(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE bench_items;")
        conn.commit()

def pg_insert(conn, n: int):
    rows = [(rand_name(i), i % 20, 1850 + (i % 200), payload_str(1)) for i in range(1, n + 1)]
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO bench_items(name, league_id, founded_year, payload) VALUES (%s,%s,%s,%s);", rows)
    conn.commit()

def pg_selects(conn, n: int):
    # pick some ids/names that exist
    pick_id = max(1, n // 2)
    pick_name = rand_name(pick_id)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM bench_items WHERE id = %s;", (pick_id,))
        cur.fetchone()
        cur.execute("SELECT * FROM bench_items WHERE name = %s;", (pick_name,))
        cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM bench_items WHERE founded_year BETWEEN %s AND %s;", (1900, 1950))
        cur.fetchone()
        cur.execute("SELECT * FROM bench_items ORDER BY founded_year DESC LIMIT 50;")
        cur.fetchall()

def pg_update(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE bench_items SET payload = %s WHERE founded_year < %s;", (payload_str(1), 1900))
    conn.commit()

def pg_delete(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM bench_items WHERE founded_year < %s;", (1900,))
    conn.commit()

# =========================
# MySQL
# =========================
MYSQL_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS bench_items (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  league_id INT NOT NULL,
  founded_year INT NOT NULL,
  payload TEXT NOT NULL
);
"""

def mysql_connect():
    cfg = parse_mysql_uri(MYSQL_URI)
    return mysql.connector.connect(**cfg)

def mysql_setup(conn, with_indexes: bool):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS bench_items;")
    cur.execute(MYSQL_TABLE_DDL)
    if with_indexes:
        cur.execute("CREATE INDEX idx_bench_name ON bench_items(name);")
        cur.execute("CREATE INDEX idx_bench_league_year ON bench_items(league_id, founded_year);")
    conn.commit()
    cur.close()

def mysql_clear(conn):
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE bench_items;")
    conn.commit()
    cur.close()

def mysql_insert(conn, n: int):
    rows = [(rand_name(i), i % 20, 1850 + (i % 200), payload_str(1)) for i in range(1, n + 1)]
    cur = conn.cursor()
    cur.executemany("INSERT INTO bench_items(name, league_id, founded_year, payload) VALUES (%s,%s,%s,%s);", rows)
    conn.commit()
    cur.close()

def mysql_selects(conn, n: int):
    pick_id = max(1, n // 2)
    pick_name = rand_name(pick_id)
    cur = conn.cursor()
    cur.execute("SELECT * FROM bench_items WHERE id = %s;", (pick_id,))
    cur.fetchone()
    cur.execute("SELECT * FROM bench_items WHERE name = %s;", (pick_name,))
    cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM bench_items WHERE founded_year BETWEEN %s AND %s;", (1900, 1950))
    cur.fetchone()
    cur.execute("SELECT * FROM bench_items ORDER BY founded_year DESC LIMIT 50;")
    cur.fetchall()
    cur.close()

def mysql_update(conn):
    cur = conn.cursor()
    cur.execute("UPDATE bench_items SET payload = %s WHERE founded_year < %s;", (payload_str(1), 1900))
    conn.commit()
    cur.close()

def mysql_delete(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM bench_items WHERE founded_year < %s;", (1900,))
    conn.commit()
    cur.close()

# =========================
# Mongo
# =========================
def mongo_connect():
    client = MongoClient(MONGO_URI)
    return client, client[MONGO_DB]

def mongo_setup(db, with_indexes: bool):
    col = db["bench_items"]
    col.drop()
    if with_indexes:
        col.create_index([("name", ASCENDING)])
        col.create_index([("league_id", ASCENDING), ("founded_year", ASCENDING)])

def mongo_clear(db):
    db["bench_items"].delete_many({})

def mongo_insert(db, n: int):
    docs = [{
        "name": rand_name(i),
        "league_id": i % 20,
        "founded_year": 1850 + (i % 200),
        "payload": payload_str(1),
    } for i in range(1, n + 1)]
    db["bench_items"].insert_many(docs, ordered=True)

def mongo_selects(db, n: int):
    col = db["bench_items"]
    # by _id is awkward because we didn't control it; so we do by "name" as point-lookup analogue
    pick_name = rand_name(max(1, n // 2))
    col.find_one({"name": pick_name})
    col.find_one({"name": pick_name})  # treat as "by id" equivalent (point lookup)
    col.count_documents({"founded_year": {"$gte": 1900, "$lte": 1950}})
    list(col.find({}).sort("founded_year", DESCENDING).limit(50))

def mongo_update(db):
    db["bench_items"].update_many({"founded_year": {"$lt": 1900}}, {"$set": {"payload": payload_str(1)}})

def mongo_delete(db):
    db["bench_items"].delete_many({"founded_year": {"$lt": 1900}})

# =========================
# Runner
# =========================
def time_op(fn) -> float:
    t0 = now()
    fn()
    t1 = now()
    return (t1 - t0) * 1000.0

def main():
    results: List[ResultRow] = []

    scenarios = [("no_index", False), ("with_index", True)]

    # Postgres
    pg = pg_connect()
    pg.autocommit = False
    for scen_name, with_idx in scenarios:
        pg_setup(pg, with_idx)
        for n in SIZES:
            for r in range(1, REPEATS + 1):
                pg_clear(pg)
                results.append(ResultRow("postgres", scen_name, n, r, "insert", time_op(lambda: pg_insert(pg, n))))
                results.append(ResultRow("postgres", scen_name, n, r, "selects", time_op(lambda: pg_selects(pg, n))))
                results.append(ResultRow("postgres", scen_name, n, r, "update", time_op(lambda: pg_update(pg))))
                results.append(ResultRow("postgres", scen_name, n, r, "delete", time_op(lambda: pg_delete(pg))))
    pg.close()

    # MySQL
    my = mysql_connect()
    for scen_name, with_idx in scenarios:
        mysql_setup(my, with_idx)
        for n in SIZES:
            for r in range(1, REPEATS + 1):
                mysql_clear(my)
                results.append(ResultRow("mysql", scen_name, n, r, "insert", time_op(lambda: mysql_insert(my, n))))
                results.append(ResultRow("mysql", scen_name, n, r, "selects", time_op(lambda: mysql_selects(my, n))))
                results.append(ResultRow("mysql", scen_name, n, r, "update", time_op(lambda: mysql_update(my))))
                results.append(ResultRow("mysql", scen_name, n, r, "delete", time_op(lambda: mysql_delete(my))))
    my.close()

    # Mongo
    mongo_client, mongo_db = mongo_connect()
    for scen_name, with_idx in scenarios:
        mongo_setup(mongo_db, with_idx)
        for n in SIZES:
            for r in range(1, REPEATS + 1):
                mongo_clear(mongo_db)
                results.append(ResultRow("mongo", scen_name, n, r, "insert", time_op(lambda: mongo_insert(mongo_db, n))))
                results.append(ResultRow("mongo", scen_name, n, r, "selects", time_op(lambda: mongo_selects(mongo_db, n))))
                results.append(ResultRow("mongo", scen_name, n, r, "update", time_op(lambda: mongo_update(mongo_db))))
                results.append(ResultRow("mongo", scen_name, n, r, "delete", time_op(lambda: mongo_delete(mongo_db))))
    mongo_client.close()

    # print CSV + averages
    print("db,scenario,n,op,avg_ms")
    for db in ["postgres", "mysql", "mongo"]:
        for scen_name, _ in scenarios:
            for n in SIZES:
                for op in ["insert", "selects", "update", "delete"]:
                    ms = [x.ms for x in results if x.db == db and x.scenario == scen_name and x.n == n and x.op == op]
                    avg = statistics.mean(ms)
                    print(f"{db},{scen_name},{n},{op},{avg:.3f}")

if __name__ == "__main__":
    main()