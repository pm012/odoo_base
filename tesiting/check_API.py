import requests, json

# Список книг
r = requests.post("http://localhost:8069/api/books",
                  json={"jsonrpc": "2.0", "method": "call", "params": {"limit": 5}, "id": None})
print(json.dumps(r.json(), indent=2, ensure_ascii=False))