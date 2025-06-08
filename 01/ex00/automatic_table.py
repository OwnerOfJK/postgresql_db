import os
from psycopg2 import sql
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_utils import connect_to_db, get_csv_files, print_tables_length, drop_tables, create_table, fill_table

def infer_columns_from_csv(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
    columns = []
    for col in header:
        col = col.strip()
        match col:
            case "event_time":
                columns.append((col, "TIMESTAMPTZ"))
            case "event_type":
                columns.append((col, "VARCHAR(100)"))
            case "product_id":
                columns.append((col, "INTEGER"))
            case "price":
                columns.append((col, "NUMERIC(10, 2)"))
            case "user_id":
                columns.append((col, "BIGINT"))
            case "user_session":
                columns.append((col, "UUID"))
            case "category_id":
                columns.append((col, "BIGINT"))
            case "category_code":
                columns.append((col, "VARCHAR(100)"))
            case "brand":
                columns.append((col, "VARCHAR(100)"))
            case _:
                columns.append((col, "TEXT"))
    return columns

def main():
    print("Starting the creation of tables from CSV files")
    data_dir = sys.argv[1]
    conn, cursor = connect_to_db()
    drop_tables(cursor, ["customers"])
    csv_files = get_csv_files(data_dir)

    table_names = []
    for file_path in csv_files:
        columns = infer_columns_from_csv(file_path)
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        table_names.append(table_name)
        create_table(cursor, table_name, columns)
        fill_table(cursor, file_path, table_name)
    
    print_tables_length(cursor)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()