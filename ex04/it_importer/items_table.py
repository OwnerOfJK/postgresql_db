import os
import pandas
import psycopg2
import time
from psycopg2 import sql

def connect_to_db():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host="db",
                port=os.getenv("POSTGRES_PORT")
            )
            cursor = conn.cursor()
            print("PostgreSQL is ready!")
            return conn, cursor
        except psycopg2.OperationalError as e:
            print(f"Waiting for PostgreSQL... ({i+1}/10)")
            time.sleep(2)
    raise Exception("PostgreSQL not ready after waiting.")

def get_csv_files(path: str):
    csv_files = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            csv_files.append(os.path.join(path, file))
    return csv_files

def infer_columns(df: pandas.DataFrame):
    columns = []
    for col in df.columns:
        match col.strip():
            case "product_id":
                columns.append((col, "INTEGER CHECK (product_id >= 0)"))
            case "category_id":
                columns.append((col, "BIGINT CHECK (category_id IS NULL OR category_id >= 0)"))
            case "category_code":
                columns.append((col, "VARCHAR(100)"))
            case "brand":
                columns.append((col, "VARCHAR(100)"))
            case _:
                columns.append((col, "TEXT"))
    return columns

def create_table(cursor, table_name: str, columns: list):
    #build the SQL string
    column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns])
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        sql.Identifier(table_name + 's'),
        sql.SQL(column_defs)
    )
    cursor.execute(query)
    print(f"Added table {table_name} with columns {columns}")

def main():
    print("Starting the script")
    data_dir = "./item"
    conn, cursor = connect_to_db();
    csv_files = get_csv_files(data_dir)

    for file_path in csv_files:
        #modify item to items, ugly
        table_name = f"{os.path.splitext(os.path.basename(file_path))[0]}s"
        df = pandas.read_csv(file_path)
        columns = infer_columns(df)
        create_table(cursor, table_name, columns)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
