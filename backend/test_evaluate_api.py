import requests
import time
import sys

def test_evaluate():
    url = "http://localhost:8000/evaluate"
    payload = {
        "question": "how do i order 7m",
        # "ground_truth": "..." # Optional for debug
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Answer:", data.get("answer"))
            contexts = data.get("contexts", [])
            print(f"Contexts: {len(contexts)}")
            for i, ctx in enumerate(contexts[:3]):
                print(f"--- Context {i+1} ---\n{ctx[:200]}...\n")
            print("Metrics:", data.get("metrics"))
        else:
            print(f"Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # fast check
    test_evaluate()
