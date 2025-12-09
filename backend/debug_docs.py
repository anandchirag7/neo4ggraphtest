import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from models.neo4j_client import _driver

def debug_neo4j_docs():
    driver = _driver()
    with driver.session() as session:
        # 1. List all Doc IDs
        print("--- All Documents ---")
        result = session.run("MATCH (d:Document) RETURN d.doc_id, d.filename, d.name")
        for r in result:
            print(f"ID: {r['d.doc_id']} | Filename: {r['d.filename']} | Name: {r['d.name']}")
            
        # 2. Check context for '7m' doc
        print("\n--- Content check for doc_id='7m' ---")
        q = """
        MATCH (d:Document {doc_id: '7m'})-[:HAS_PAGE]->(p:Page)
        RETURN p.page_number, p.text
        LIMIT 2
        """
        result = session.run(q)
        found = False
        for r in result:
            found = True
            text_content = r['p.text'] or "NO_TEXT"
            print(f"Page {r['p.page_number']}: {text_content[:100]}...")
            
        if not found:
            print("No pages found for doc_id='7m'")
            
    driver.close()

if __name__ == "__main__":
    debug_neo4j_docs()
