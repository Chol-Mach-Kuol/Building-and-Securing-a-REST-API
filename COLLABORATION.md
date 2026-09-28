# Team Collaboration Guide — Building and Securing a REST API

## Team Structure

| Role | Member |
|------|--------|
| Team Lead + Data Parsing | Chol Mach |
| API Implementation | Kuol Akech |
| Authentication & Security | Abay Tessema |
| DSA + Documentation + Testing | Alier Akuang |

---

## ✅ CHOL MACH — Team Lead + Data Parsing (COMPLETED)

**Status: Done and pushed to `main`**

Chol has already completed:
- Set up the GitHub repository and all folders (`api/`, `dsa/`, `docs/`, `screenshots/`)
- Written `dsa/parse_xml.py` — parses all 1,691 SMS records into JSON
- Written `README.md` with full setup and curl instructions
- Pushed `modified_sms_v2.xml` to the repo

**Ongoing responsibilities:**
- Review and merge all Pull Requests from teammates
- Maintain the Scrum Board on GitHub Projects
- Fill out the team participation sheet
- Assemble the final PDF report introduction and conclusion

---

---

## 👤 KUOL AKECH — API Implementation

### Step 1 — Clone the repo and create your branch
```bash
git clone https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API.git
cd Building-and-Securing-a-REST-API
git checkout -b feature/kuol-api
```

### Step 2 — Create the file `api/server.py` with this code

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from dsa.parse_xml import parse_sms_xml

XML_PATH = os.path.join(os.path.dirname(__file__), '..', 'modified_sms_v2.xml')
transactions = parse_sms_xml(XML_PATH)
next_id = [max(t['id'] for t in transactions) + 1]


def send_json(handler, status, data):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(body)


class APIHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/transactions':
            send_json(self, 200, transactions)
        elif self.path.startswith('/transactions/'):
            try:
                tid = int(self.path.split('/')[-1])
                match = next((t for t in transactions if t['id'] == tid), None)
                if match:
                    send_json(self, 200, match)
                else:
                    send_json(self, 404, {'error': 'Transaction not found'})
            except ValueError:
                send_json(self, 400, {'error': 'Invalid ID'})
        else:
            send_json(self, 404, {'error': 'Not found'})

    def do_POST(self):
        if self.path == '/transactions':
            length = int(self.headers.get('Content-Length', 0))
            try:
                body = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                send_json(self, 400, {'error': 'Invalid JSON'})
                return
            body['id'] = next_id[0]
            next_id[0] += 1
            transactions.append(body)
            send_json(self, 201, body)
        else:
            send_json(self, 404, {'error': 'Not found'})

    def do_PUT(self):
        if self.path.startswith('/transactions/'):
            try:
                tid = int(self.path.split('/')[-1])
            except ValueError:
                send_json(self, 400, {'error': 'Invalid ID'})
                return
            match = next((t for t in transactions if t['id'] == tid), None)
            if not match:
                send_json(self, 404, {'error': 'Transaction not found'})
                return
            length = int(self.headers.get('Content-Length', 0))
            try:
                body = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                send_json(self, 400, {'error': 'Invalid JSON'})
                return
            match.update(body)
            send_json(self, 200, match)
        else:
            send_json(self, 404, {'error': 'Not found'})

    def do_DELETE(self):
        if self.path.startswith('/transactions/'):
            try:
                tid = int(self.path.split('/')[-1])
            except ValueError:
                send_json(self, 400, {'error': 'Invalid ID'})
                return
            match = next((t for t in transactions if t['id'] == tid), None)
            if not match:
                send_json(self, 404, {'error': 'Transaction not found'})
                return
            transactions.remove(match)
            send_json(self, 200, {'message': f'Transaction {tid} deleted'})
        else:
            send_json(self, 404, {'error': 'Not found'})


if __name__ == '__main__':
    server = HTTPServer(('', 8000), APIHandler)
    print('Server running on http://localhost:8000')
    server.serve_forever()
```

### Step 3 — Test it locally before pushing
```bash
# Terminal 1 — start the server
python3 api/server.py

# Terminal 2 — test endpoints
curl http://localhost:8000/transactions
curl http://localhost:8000/transactions/1
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","amount":5000,"sender":"self","receiver":"Jane Smith","fee":100,"balance_after":3000,"timestamp":"2024-05-10 10:00:00"}'
curl -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount":9999}'
curl -X DELETE http://localhost:8000/transactions/1
```

### Step 4 — Commit and push your branch
```bash
git add api/server.py
git commit -m "Kuol Akech: Add CRUD API endpoints"
git push origin feature/kuol-api
```

### Step 5 — Open a Pull Request
Go to https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API and open a Pull Request from `feature/kuol-api` → `main`. Tag Chol Mach to review and merge.

> **Note:** Abay will add auth on top of your server.py after your PR is merged. Do NOT add auth yourself.

---

---

## 👤 ABAY TESSEMA — Authentication & Security

> **Wait for Kuol's PR to be merged into `main` before starting.**

### Step 1 — Clone/pull the latest main and create your branch
```bash
git clone https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API.git
cd Building-and-Securing-a-REST-API
# If already cloned:
git checkout main
git pull origin main
git checkout -b feature/abay-auth
```

### Step 2 — Create `api/auth.py` with this code

```python
import base64


VALID_USERNAME = 'admin'
VALID_PASSWORD = 'momo2024'


def check_auth(handler):
    auth_header = handler.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        _reject(handler)
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
        username, password = decoded.split(':', 1)
    except Exception:
        _reject(handler)
        return False
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return True
    _reject(handler)
    return False


def _reject(handler):
    body = b'{"error": "Unauthorized"}'
    handler.send_response(401)
    handler.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(body)
```

### Step 3 — Update `api/server.py` to use auth

Add this import at the top of `api/server.py` (after the existing imports):
```python
from api.auth import check_auth
```

Then add `if not check_auth(self): return` as the **first line** inside every method (`do_GET`, `do_POST`, `do_PUT`, `do_DELETE`). Example:

```python
def do_GET(self):
    if not check_auth(self):
        return
    # ... rest of existing code unchanged
```

Do the same for `do_POST`, `do_PUT`, and `do_DELETE`.

### Step 4 — Test authentication with curl

Start the server first:
```bash
python3 api/server.py
```

Then run these three tests and take a screenshot of each:

```bash
# Test 1 — valid credentials (should return 200 with data)
curl -u admin:momo2024 http://localhost:8000/transactions

# Test 2 — wrong password (should return 401)
curl -u admin:wrongpassword http://localhost:8000/transactions

# Test 3 — no credentials (should return 401)
curl http://localhost:8000/transactions
```

Save screenshots as:
- `screenshots/auth_success.png`
- `screenshots/auth_fail_wrong.png`
- `screenshots/auth_fail_none.png`

### Step 5 — Commit and push
```bash
git add api/auth.py api/server.py screenshots/
git commit -m "Abay Tessema: Add Basic Auth middleware and security screenshots"
git push origin feature/abay-auth
```

### Step 6 — Open a Pull Request
Go to https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API and open a Pull Request from `feature/abay-auth` → `main`. Tag Chol Mach to review and merge.

### Step 7 — Write your PDF report section

Write the following in the shared PDF report:

**Introduction to API Security**
- Explain what API security means and why it matters

**How Basic Auth Works**
- The client sends `username:password` encoded in Base64 with every request
- Example: `Authorization: Basic YWRtaW46bW9tbzIwMjQ=`
- Base64 is encoding, NOT encryption — anyone can decode it instantly

**Why Basic Auth is Weak**
- Credentials are sent with every single request
- Base64 is fully reversible — not secure on its own
- Vulnerable to interception if HTTPS is not used
- No token expiry — stolen credentials work forever
- No way to revoke access without changing the password

**Stronger Alternatives**
- **JWT (JSON Web Tokens):** Server issues a signed token after login. Client sends the token (not the password) in future requests. Tokens expire automatically and can be revoked.
- **OAuth2:** Industry standard for delegated access. Used by Google, GitHub, etc. Supports scopes, refresh tokens, and third-party login flows.

**Recommendation:** Always use HTTPS with any authentication method to encrypt data in transit.

---

---

## 👤 ALIER AKUANG — DSA + Documentation + Testing

> **Wait for Abay's PR to be merged into `main` before taking final screenshots. You can write the DSA code and docs in parallel.**

### Step 1 — Clone/pull the latest main and create your branch
```bash
git clone https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API.git
cd Building-and-Securing-a-REST-API
# If already cloned:
git checkout main
git pull origin main
git checkout -b feature/alier-dsa
```

### Step 2 — Create `dsa/search.py` with this code

```python
import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dsa.parse_xml import parse_sms_xml

XML_PATH = os.path.join(os.path.dirname(__file__), '..', 'modified_sms_v2.xml')
transactions = parse_sms_xml(XML_PATH)


def linear_search(transactions, target_id):
    for t in transactions:
        if t['id'] == target_id:
            return t
    return None


def build_lookup_dict(transactions):
    return {t['id']: t for t in transactions}


def dict_lookup(lookup, target_id):
    return lookup.get(target_id)


if __name__ == '__main__':
    target_id = 20
    runs = 1000

    # Linear Search timing
    start = time.perf_counter()
    for _ in range(runs):
        result = linear_search(transactions, target_id)
    linear_time = (time.perf_counter() - start) / runs

    # Dictionary Lookup timing
    lookup = build_lookup_dict(transactions)
    start = time.perf_counter()
    for _ in range(runs):
        result = dict_lookup(lookup, target_id)
    dict_time = (time.perf_counter() - start) / runs

    print(f"Dataset size       : {len(transactions)} records")
    print(f"Target ID          : {target_id}")
    print(f"Linear Search time : {linear_time:.8f} seconds (avg over {runs} runs)")
    print(f"Dict Lookup time   : {dict_time:.8f} seconds (avg over {runs} runs)")
    print(f"Speedup            : {linear_time / dict_time:.1f}x faster with dict")
    print()
    print("--- Reflection ---")
    print("Linear Search is O(n): it checks every record until it finds a match.")
    print("Dictionary Lookup is O(1): it jumps directly to the value using a hash key.")
    print("With 1,691 records, dict lookup is significantly faster.")
    print()
    print("Other data structures that could improve efficiency:")
    print("- Binary Search on a sorted list: O(log n) — faster than linear but requires sorting first.")
    print("- Hash Map (same as Python dict): O(1) average — best for direct ID lookups.")
    print("- B-Tree (used in databases): O(log n) — efficient for range queries and sorted access.")
```

### Step 3 — Run and verify the DSA script
```bash
python3 dsa/search.py
```

You should see a timing comparison table printed. Take note of the output for your PDF report.

### Step 4 — Create `docs/api_docs.md` with this content

```markdown
# API Documentation — MTN MoMo Transactions

Base URL: `http://localhost:8000`
Authentication: Basic Auth required on all endpoints
Credentials: username `admin`, password `momo2024`

---

## Endpoints

### GET /transactions
Returns all transactions.

**Request:**
```
GET /transactions
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
```

**Response 200:**
```json
[
  {
    "id": 1,
    "type": "incoming",
    "amount": 2000,
    "sender": "Jane Smith",
    "receiver": null,
    "fee": 0,
    "balance_after": 2000,
    "timestamp": "10 May 2024 4:30:58 PM"
  }
]
```

---

### GET /transactions/{id}
Returns a single transaction by ID.

**Request:**
```
GET /transactions/1
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
```

**Response 200:**
```json
{
  "id": 1,
  "type": "incoming",
  "amount": 2000,
  "sender": "Jane Smith",
  "receiver": null,
  "fee": 0,
  "balance_after": 2000,
  "timestamp": "10 May 2024 4:30:58 PM"
}
```

**Response 404:**
```json
{ "error": "Transaction not found" }
```

---

### POST /transactions
Adds a new transaction.

**Request:**
```
POST /transactions
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
Content-Type: application/json
```
```json
{
  "type": "payment",
  "amount": 5000,
  "sender": "self",
  "receiver": "Jane Smith",
  "fee": 100,
  "balance_after": 3000,
  "timestamp": "2024-05-10 10:00:00"
}
```

**Response 201:**
```json
{
  "id": 1692,
  "type": "payment",
  "amount": 5000,
  "sender": "self",
  "receiver": "Jane Smith",
  "fee": 100,
  "balance_after": 3000,
  "timestamp": "2024-05-10 10:00:00"
}
```

---

### PUT /transactions/{id}
Updates an existing transaction by ID.

**Request:**
```
PUT /transactions/1
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
Content-Type: application/json
```
```json
{ "amount": 9999 }
```

**Response 200:**
```json
{ "id": 1, "amount": 9999, ... }
```

**Response 404:**
```json
{ "error": "Transaction not found" }
```

---

### DELETE /transactions/{id}
Deletes a transaction by ID.

**Request:**
```
DELETE /transactions/1
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
```

**Response 200:**
```json
{ "message": "Transaction 1 deleted" }
```

**Response 404:**
```json
{ "error": "Transaction not found" }
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK — request succeeded |
| 201 | Created — new record added |
| 400 | Bad Request — malformed JSON or invalid ID |
| 401 | Unauthorized — missing or wrong credentials |
| 404 | Not Found — transaction ID does not exist |
```

### Step 5 — Test all endpoints and take screenshots

Make sure the server is running with auth enabled (after Abay's PR is merged):
```bash
python3 api/server.py
```

Run each command below and take a screenshot of the terminal output:

```bash
# GET all — save as screenshots/get_all.png
curl -u admin:momo2024 http://localhost:8000/transactions

# GET one — save as screenshots/get_one.png
curl -u admin:momo2024 http://localhost:8000/transactions/1

# POST — save as screenshots/post_test.png
curl -u admin:momo2024 -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","amount":5000,"sender":"self","receiver":"Jane Smith","fee":100,"balance_after":3000,"timestamp":"2024-05-10 10:00:00"}'

# PUT — save as screenshots/put_test.png
curl -u admin:momo2024 -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount":9999}'

# DELETE — save as screenshots/delete_test.png
curl -u admin:momo2024 -X DELETE http://localhost:8000/transactions/1
```

### Step 6 — Commit and push
```bash
git add dsa/search.py docs/api_docs.md screenshots/
git commit -m "Alier Akuang: Add DSA search comparison, API docs, and test screenshots"
git push origin feature/alier-dsa
```

### Step 7 — Open a Pull Request
Go to https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API and open a Pull Request from `feature/alier-dsa` → `main`. Tag Chol Mach to review and merge.

### Step 8 — Write your PDF report section

**DSA Comparison Results**
- Include the printed output from running `python3 dsa/search.py`
- Explain the numbers: linear search scans every record (O(n)), dict lookup uses a hash key (O(1))
- With 1,691 records, dict lookup is many times faster

**Reflection**
- Linear Search: simple but slow for large datasets — time grows with dataset size
- Dictionary Lookup: constant time regardless of dataset size — best for ID-based lookups
- Binary Search: O(log n) — good alternative if data is sorted and memory is limited
- B-Tree: used in databases for indexed lookups — handles range queries efficiently

---

---

## Repository Structure

```
Building-and-Securing-a-REST-API/
├── api/
│   ├── server.py              ← Kuol Akech
│   └── auth.py                ← Abay Tessema
├── dsa/
│   ├── parse_xml.py           ← Chol Mach ✅
│   └── search.py              ← Alier Akuang
├── docs/
│   └── api_docs.md            ← Alier Akuang
├── screenshots/
│   ├── auth_success.png       ← Abay Tessema
│   ├── auth_fail_wrong.png    ← Abay Tessema
│   ├── auth_fail_none.png     ← Abay Tessema
│   ├── get_all.png            ← Alier Akuang
│   ├── get_one.png            ← Alier Akuang
│   ├── post_test.png          ← Alier Akuang
│   ├── put_test.png           ← Alier Akuang
│   └── delete_test.png        ← Alier Akuang
├── modified_sms_v2.xml        ← Chol Mach ✅
├── README.md                  ← Chol Mach ✅
└── COLLABORATION.md           ← this file
```

---

## Merge Order (Important)

```
Kuol's PR → merged first
Abay's PR → merged second (depends on Kuol's server.py)
Alier's PR → merged last (tests the final combined server)
```

---

## Deadlines (internal — before Tuesday 11:59pm)

| Milestone | Owner | Internal Deadline |
|-----------|-------|-------------------|
| Repo setup + XML parser | Chol Mach | ✅ Done |
| CRUD API endpoints | Kuol Akech | Day 3 |
| Basic Auth + screenshots | Abay Tessema | Day 4 |
| DSA + docs + all test screenshots | Alier Akuang | Day 5 |
| PDF report fully assembled | All | Day 6 |
| Final review & submission | Chol Mach | Day 7 (Tuesday) |

---

## PDF Report — Who Writes What

| Section | Owner |
|---------|-------|
| Introduction & conclusion | Chol Mach |
| Endpoint documentation | Alier Akuang |
| DSA comparison results & reflection | Alier Akuang |
| Introduction to API security | Abay Tessema |
| Basic Auth limitations & alternatives (JWT, OAuth2) | Abay Tessema |

---

## Notes

- Every member **must** have real commits in the GitHub repo — no commits = 0 multiplier on your individual grade.
- Screenshots must be real (taken from your own terminal/Postman), not copied from online.
- The team participation sheet is Chol Mach's responsibility — all sections must be fully completed.
- Other members are added to the participation sheet with **comment-only** access — do not edit it directly.
- If you are stuck, open a GitHub Issue and tag your teammate rather than going silent.
