# MoMo SMS Transactions — REST API

**Owner**: Kuol Akech  
**File**: `api/server.py`

## Run

```bash
python api/server.py          # http://localhost:8000
PORT=9000 python api/server.py
```

## Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/transactions` | List all transactions | 200 |
| GET | `/transactions/{id}` | Get one transaction | 200 / 404 |
| POST | `/transactions` | Create a transaction | 201 / 400 |
| PUT | `/transactions/{id}` | Update a transaction | 200 / 400 / 404 |
| DELETE | `/transactions/{id}` | Delete a transaction | 200 / 404 |

## Design

- **TransactionStore**: dict-based `{id: record}` for O(1) lookup vs O(n) list scan
- **Thread-safe**: `threading.Lock` on all write operations
- **Auth**: integrates with `api/auth.py` (`check_auth`), falls back gracefully if missing
- **Data**: loads from `dsa/parse_xml.py` → `modified_sms_v2.xml`

## Example

```bash
# List all
curl http://localhost:8000/transactions

# Get one
curl http://localhost:8000/transactions/1

# Create
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"body": "You have received 500 RWF", "address": "+250788000000"}'

# Update
curl -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"body": "Updated body"}'

# Delete
curl -X DELETE http://localhost:8000/transactions/1
```
