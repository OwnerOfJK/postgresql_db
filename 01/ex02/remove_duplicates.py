from psycopg2 import sql
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_utils import connect_to_db, get_existing_tables, drop_tables, replace_table, print_entries, print_tables_length

def remove_duplicates(cursor, table_name):
    cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} AS
        SELECT DISTINCT * FROM {};
    """).format(
        sql.Identifier(f"{table_name}_no_duplicates"),
        sql.Identifier(table_name)
    ))
    print(f"Created '{table_name}_no_duplicates' table with distinct rows.")

def filter_for_dup_dates(cursor, table_name):
    cursor.execute(sql.SQL("""
        WITH FlaggedDuplicates AS (
            SELECT ctid, *,
                LAG(event_time) OVER (
                    PARTITION BY event_type, product_id, user_id
                    ORDER BY event_time
                ) AS prev_event_time
            FROM {}
        ),
        ToDelete AS (
            SELECT ctid
            FROM FlaggedDuplicates
            WHERE prev_event_time IS NOT NULL
            AND EXTRACT(EPOCH FROM (event_time - prev_event_time)) <= 1
        )
        DELETE FROM {}
        WHERE ctid IN (SELECT ctid FROM ToDelete);
    """).format(
        sql.Identifier(table_name),
        sql.Identifier(table_name),
    ))
    print(f"Remove all non distinct user_id rows in {table_name}.")

def main():
    print("Starting the removal of duplicates")
    conn, cursor = connect_to_db()
    drop_tables(cursor, ["customers_no_duplicates"])
    
    remove_duplicates(cursor, 'customers')
    print_tables_length(cursor, ['customers_no_duplicates'])
    filter_for_dup_dates(cursor, 'customers_no_duplicates')
    replace_table(cursor, 'customers', 'customers_no_duplicates')
    print_tables_length(cursor)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()