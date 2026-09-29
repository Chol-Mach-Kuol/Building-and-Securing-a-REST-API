"""
MoMo SMS Transactions - REST API (plain Python, no frameworks)
Owner: Kuol Akech

Endpoints
---------
    GET    /transactions          -> list all transactions            (200)
    GET    /transactions/{id}     -> one transaction                  (200 / 404)
    POST   /transactions          -> create a transaction             (201 / 400)
    PUT    /transactions/{id}     -> update a transaction             (200 / 400 / 404)
    DELETE /transactions/{id}     -> delete a transaction             (200 / 404)

Run
---
    python api/server.py              # http://localhost:8000
    PORT=9000 python api/server.py    # another port

Team integration
----------------
    * Data  : loaded from Chol's  dsa/parse_xml.py
    * Auth  : every request calls Abay's  api/auth.py -> check_auth(handler)
"""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from api.auth import check_auth

# --------------------------------------------------------------------------
# Paths so we can import from dsa/ and api/ no matter where we run from
# --------------------------------------------------------------------------
API_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(API_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "dsa"))
sys.path.insert(0, API_DIR)

XML_PATH = os.path.join(ROOT_DIR, "modified_sms_v2.xml")

# --------------------------------------------------------------------------
# Authentication (Abay's auth.py)
# Until auth.py is merged the server still runs, so the endpoints can be
# built and tested first, as agreed in the team plan.
# --------------------------------------------------------------------------
try:
    from auth import check_auth
    AUTH_ENABLED = True
except ImportError:
    AUTH_ENABLED = False

    def check_auth(handler):  # placeholder until auth.py exists
        return True


# --------------------------------------------------------------------------
# Data loading (Chol's parse_xml.py)
# --------------------------------------------------------------------------
def load_transactions():
    """Return the parsed SMS records as a list of dicts."""
    import parse_xml

    try:
        records = parse_xml.parse_sms_xml(XML_PATH)
    except TypeError:          # parser takes no arguments
        records = parse_xml.parse_sms_xml()
    return records


# --------------------------------------------------------------------------
# In-memory data store
# A dict {id: transaction} gives O(1) lookup for /transactions/{id}
# instead of scanning the whole list (see the DSA part of the project).
# --------------------------------------------------------------------------
class TransactionStore:
    def __init__(self, records):
        self._lock = threading.Lock()   # server handles requests in threads
        self._data = {}
        for i, record in enumerate(records, start=1):
            # Normalise id to int - parse_xml may return string attributes
            rid = int(record["id"]) if "id" in record else i
            self._data[rid] = {**record, "id": rid}
        self._next_id = max(self._data, default=0) + 1

    def all(self):
        return list(self._data.values())

    def get(self, tx_id):
        return self._data.get(tx_id)

    def add(self, fields):
        with self._lock:
            record = {"id": self._next_id, **fields}
            self._data[record["id"]] = record
            self._next_id += 1
            return record

    def update(self, tx_id, fields):
        with self._lock:
            record = self._data.get(tx_id)
            if record is None:
                return None
            record.update(fields)
            return record

    def delete(self, tx_id):
        with self._lock:
            return self._data.pop(tx_id, None)

    def __len__(self):
        return len(self._data)


class BadRequest(Exception):
    """Raised for anything that should become a 400 response."""


def validate_body(body):
    """Check a POST/PUT body and return it, or raise BadRequest."""
    if not isinstance(body, dict):
        raise BadRequest("Request body must be a JSON object")
    if not body:
        raise BadRequest("Request body cannot be empty")
    if "id" in body:
        raise BadRequest("'id' is assigned by the server and cannot be set")
    if "amount" in body:
        amount = body["amount"]
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise BadRequest("'amount' must be a number")
        if amount < 0:
            raise BadRequest("'amount' cannot be negative")
    return body


# --------------------------------------------------------------------------
# Request handler
# --------------------------------------------------------------------------
class TransactionHandler(BaseHTTPRequestHandler):
    store = None  # set in run()

    # ---------- response helpers ----------
    def send_json(self, status, data, headers=None):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json(status, {"error": message})

    # ---------- request helpers ----------
    def is_authorized(self):
        """Call Abay's check_auth. Sends the 401 response if it fails."""
        if check_auth(self):
            return True
        self.send_json(401, {"error": "Unauthorized"},
                       {"WWW-Authenticate": 'Basic realm="MoMo API"'})
        return False

    def parse_path(self):
        """
        Split the URL into (resource, id):
            /transactions     -> ("transactions", None)
            /transactions/5   -> ("transactions", 5)
        Raises LookupError for unknown routes, ValueError for a non-number id.
        """
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if not parts or parts[0] != "transactions" or len(parts) > 2:
            raise LookupError
        if len(parts) == 1:
            return None
        return int(parts[1])   # ValueError if not a number

    def read_json(self):
        """Read and decode the JSON request body, or raise BadRequest."""
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            raise BadRequest("Request body is required")
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise BadRequest("Invalid JSON in request body")

    def handle_request(self, action):
        """
        Shared flow for every method:
        1. auth check  2. route  3. run the action  4. turn errors into JSON
        """
        if not self.is_authorized():
            return
        try:
            tx_id = self.parse_path()
        except LookupError:
            return self.send_error_json(404, "Endpoint not found")
        except ValueError:
            return self.send_error_json(400, "Transaction id must be a number")
        try:
            action(tx_id)
        except BadRequest as err:
            self.send_error_json(400, str(err))

    # ---------- GET ----------
    def do_GET(self):
        if not check_auth(self):
            return
        def action(tx_id):
            if tx_id is None:
                return self.send_json(200, self.store.all())
            record = self.store.get(tx_id)
            if record is None:
                return self.send_error_json(404, f"Transaction {tx_id} not found")
            self.send_json(200, record)
        self.handle_request(action)

    # ---------- POST ----------
    def do_POST(self):
        if not check_auth(self):
            return
        def action(tx_id):
            if tx_id is not None:
                return self.send_error_json(405, "Use POST /transactions to create")
            fields = validate_body(self.read_json())
            record = self.store.add(fields)
            self.send_json(201, record, {"Location": f"/transactions/{record['id']}"})
        self.handle_request(action)

    # ---------- PUT ----------
    def do_PUT(self):
        if not check_auth(self):
            return
        def action(tx_id):
            if tx_id is None:
                return self.send_error_json(405, "Use PUT /transactions/{id} to update")
            fields = validate_body(self.read_json())
            record = self.store.update(tx_id, fields)
            if record is None:
                return self.send_error_json(404, f"Transaction {tx_id} not found")
            self.send_json(200, record)
        self.handle_request(action)

    # ---------- DELETE ----------
    def do_DELETE(self):
        if not check_auth(self):
            return
        def action(tx_id):
            if tx_id is None:
                return self.send_error_json(405, "Use DELETE /transactions/{id} to delete")
            record = self.store.delete(tx_id)
            if record is None:
                return self.send_error_json(404, f"Transaction {tx_id} not found")
            self.send_json(200, {"message": f"Transaction {tx_id} deleted", "deleted": record})
        self.handle_request(action)


# --------------------------------------------------------------------------
# Start the server
# --------------------------------------------------------------------------
def run(port=8000, records=None):
    if records is None:
        records = load_transactions()
    TransactionHandler.store = TransactionStore(records)
    server = ThreadingHTTPServer(("0.0.0.0", port), TransactionHandler)

    print(f"Loaded {len(TransactionHandler.store)} transactions")
    if not AUTH_ENABLED:
        print("WARNING: api/auth.py not found - authentication is OFF")
    print(f"Server running on http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    run(port=int(os.environ.get("PORT", 8000)))
