import sys
import os
from psycopg2 import sql
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_utils import connect_to_db, print_tables_length, create_table, fill_table, get_csv_files, print_entries, replace_table, drop_tables

def left_join(cursor, table_name: str, table1: str, table2: str, join_column: str):
    query = sql.SQL("""
        CREATE TABLE {name} AS
        WITH {dedup_name} AS (
            SELECT DISTINCT ON ({col}) *
            FROM {table2}
        )
        SELECT  {table1}.event_time,
                {table1}.event_type,
                {table1}.product_id,
                {table1}.price,
                {table1}.user_id,
                {table1}.user_session,
                {dedup_name}.category_id,
                {dedup_name}.category_code,
                {dedup_name}.brand
        FROM {table1}
        LEFT JOIN {dedup_name}
        ON {table1}.{col} = {dedup_name}.{col}
    """).format(
        name=sql.Identifier(table_name),
        table1=sql.Identifier(table1),
        table2=sql.Identifier(table2),
        dedup_name=sql.Identifier("item_dedup"),
        col=sql.Identifier(join_column)
    )

    cursor.execute(query)
    print(f"Joined table {table1} and {table2} (deduplicated) with left join on '{join_column}'.")

def main():
    print("Starting the fusion of customers and item tables")
    conn, cursor = connect_to_db()
    drop_tables(cursor, ['item'])
    path = get_csv_files("./item")
    create_table(cursor, 'item', [
        ('product_id', 'INTEGER'),
        ('category_id', 'BIGINT'),
        ('category_code', 'VARCHAR(100)'),
        ('brand', 'VARCHAR(100)')
    ])
    fill_table(cursor, path[0], "item")
    print_tables_length(cursor, ['customers', 'item'])
    left_join(cursor, 'customer_item_join','customers', 'item', 'product_id')
    replace_table(cursor, 'customers', 'customer_item_join')
    print_tables_length(cursor, ['customers', 'item'])
    print_entries(cursor, 'customers', 10)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()