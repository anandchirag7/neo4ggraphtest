import psycopg2
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS

def drop_table():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASS,
        )
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS rag_chunks;")
        conn.commit()
        cur.close()
        conn.close()
        print("Table rag_chunks dropped successfully.")
    except Exception as e:
        print(f"Error dropping table: {e}")

if __name__ == "__main__":
    drop_table()
