import requests
import os
import psycopg2
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS

FILE_PATH = r"d:/AppsRepository/invoice_generator/Enterprise_kb_app/7m.pdf"
BASE_URL = "http://127.0.0.1:8002"

def upload_pdf():
    print(f"Uploading {FILE_PATH}...")
    url = f"{BASE_URL}/upload_pdf"
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return None

    with open(FILE_PATH, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                data = response.json()
                print(f"Upload success! Doc ID: {data['doc_id']}")
                return data['doc_id']
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error uploading: {e}")
            return None

def verify_neo4j(doc_id):
    print(f"Verifying Neo4j graph for {doc_id}...")
    url = f"{BASE_URL}/graph/{doc_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            links = data.get("links", [])
            print(f"Neo4j Graph: {len(nodes)} nodes, {len(links)} links.")
            if len(nodes) > 0:
                print("Neo4j verification PASSED.")
            else:
                print("Neo4j verification WARNING: No nodes found.")
        else:
            print(f"Neo4j verification FAILED: {response.status_code}")
    except Exception as e:
        print(f"Error verifying Neo4j: {e}")

def verify_postgres(doc_id):
    print(f"Verifying Postgres chunks for {doc_id}...")
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASS,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rag_chunks WHERE doc_id = %s", (doc_id,))
        count = cur.fetchone()[0]
        print(f"Postgres: Found {count} chunks for doc_id {doc_id}.")
        if count > 0:
            print("Postgres verification PASSED.")
        else:
            print("Postgres verification WARNING: No chunks found.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error verifying Postgres: {e}")

if __name__ == "__main__":
    doc_id = upload_pdf()
    if doc_id:
        verify_neo4j(doc_id)
        verify_postgres(doc_id)
    else:
        print("Skipping verification due to upload failure.")
