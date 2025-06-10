import os
import psycopg2
import time
from psycopg2 import sql
import dotenv

def connect_to_db():
    dotenv.load_dotenv()
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host="localhost",
                port=os.getenv("POSTGRES_PORT")
            )
            cursor = conn.cursor()
            print("PostgreSQL is ready!")
            return conn, cursor
        except psycopg2.OperationalError as e:
            print(f"Waiting for PostgreSQL... ({i+1}/10)")
            time.sleep(2)
    raise Exception("PostgreSQL not ready after waiting.")

def drop_tables(cursor, table_names=None):
    if table_names is None:
        table_names = get_existing_tables(cursor)
    for table in table_names:
        cursor.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table)))
        print(f"Dropped table: {table}")

def get_existing_tables(cursor, exclude_table=None):
    if exclude_table:
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
              AND TABLE_SCHEMA = 'public' 
              AND TABLE_NAME != %s;
        """, (exclude_table,))
    else:
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
              AND TABLE_SCHEMA = 'public';
        """)
    
    return [row[0] for row in cursor.fetchall()]

def print_tables_length(cursor, table_names=None):
    if table_names is None:
        table_names = get_existing_tables(cursor)
    for table in table_names:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"Table {table} has {count} rows")

def get_csv_files(path: str):
    csv_files = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            csv_files.append(os.path.join(path, file))
    return csv_files

def replace_table(cursor, old: str, new: str):
    cursor.execute(
        sql.SQL("DROP TABLE IF EXISTS {}")
        .format(sql.Identifier(old))
    )
    cursor.execute(
        sql.SQL("ALTER TABLE {} RENAME TO {}")
        .format(sql.Identifier(new), sql.Identifier(old))
    )
    print(f"Replaced table '{old}' with '{new}'")

def print_entries(cursor, table_name: str, limit: int = 10):
    cursor.execute(sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table_name)), [limit])
    rows = cursor.fetchall()
    print(f"Entries in table '{table_name}':")
    for row in rows:
        print(row)

def fill_table(cursor, file_path: str, table_name: str):
    with open(file_path, "r", encoding="utf-8") as f:
        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
    print(f"Loaded data from '{file_path}' into '{table_name}' using COPY")

def create_table(cursor, table_name: str, columns: list):
    column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns])
    drop_tables(cursor, [table_name])
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        sql.Identifier(table_name),
        sql.SQL(column_defs)
    )
    cursor.execute(query)
    print(f"Added table {table_name} with columns {columns}")