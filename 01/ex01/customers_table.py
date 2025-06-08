from psycopg2 import sql
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_utils import connect_to_db, get_existing_tables, print_tables_length, drop_tables

def create_union(cursor, tables_names: list):
    select_statements = [
        sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
        for table in tables_names
    ]
    union_query = sql.SQL(" UNION ALL ").join(select_statements)
    full_query = sql.SQL("CREATE TABLE customers AS {}").format(union_query)
    cursor.execute(full_query)
    print("Created union table 'customers' with data from existing tables.")

def main():
    print("Starting the union")
    conn, cursor = connect_to_db();
    drop_tables(cursor, ["customers"])
    table_names = get_existing_tables(cursor, exclude_table="item")
    print(f"Found tables: {table_names}")
    create_union(cursor, table_names)
    print_tables_length(cursor)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()