import json
from datetime import datetime
import pytz
import psycopg2
from functools import reduce
from db_info import db_host, db_name, db_port, db_username, db_password

# load and parsing json data  -->  name, cpu and memory usage, created_at, status and IP address

with open('sample-data.json') as json_file:
    data = json.load(json_file)

data_for_db_sub = []
data_for_db = []
dt_str = []
format_time = "%Y-%m-%dT%H:%M:%S%f%z"


def deep_get(dictionary, keys, default="unavailable data"):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)


for container in data:
    data_for_db_sub.append(deep_get(container, "name"))
    data_for_db_sub.append(deep_get(container, "state.cpu.usage"))
    data_for_db_sub.append(deep_get(container, "state.memory.usage"))
    print("created at get:", deep_get(container, "created_at"))
    # Convert local datetime to UTC time-zone datetime
    dt_str.append(deep_get(container, "created_at"))
    local_dt = datetime.strptime(dt_str[0], format_time)
    dt_utc = local_dt.astimezone(pytz.UTC)
    dt_utc_str = dt_utc.strftime(format_time)
    data_for_db_sub.append(dt_utc_str)
    dt_str.clear()
    data_for_db_sub.append(deep_get(container, "status"))

    addresses_get = (deep_get(container, "state.network.eth0.addresses"))
    data_for_db_sub.append(deep_get(addresses_get[0], "address"))

    data_for_db.append(tuple(data_for_db_sub))
    data_for_db_sub.clear()

# import parsing data to database

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_username,
    password=db_password,

)

print(connection.closed)  # 0
cursor = connection.cursor()
cursor.execute("""
    DROP TABLE IF EXISTS parsing_data;
    CREATE TABLE parsing_data (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cpu_usage TEXT NOT NULL,
    memory_usage TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    ip_address TEXT NOT NULL )
    """)

query = """
    INSERT INTO parsing_data(
    name,
    cpu_usage,
    memory_usage,
    created_at,
    status,
    ip_address

    )
    VALUES (%s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, data_for_db)
connection.commit()
connection.close()