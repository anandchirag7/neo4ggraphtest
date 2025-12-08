import requests
import os

file_path = r"d:/AppsRepository/invoice_generator/Enterprise_kb_app/7m.pdf"
url = "http://127.0.0.1:8002/upload_pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "rb") as f:
    files = {"file": f}
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
