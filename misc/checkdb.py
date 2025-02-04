import sqlite3

# connect to the database
conn = sqlite3.connect("database/tastebuddies.db")
cursor = conn.cursor()

# get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# iterate through tables and fetch all data
for table in tables:
    table_name = table[0]
    print(f"\n--- Data from {table_name} ---")
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # print column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    print(columns)
    
    # print rows
    for row in rows:
        print(row)

# close connection
conn.close()
