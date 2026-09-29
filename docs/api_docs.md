# API Documentation — MTN MoMo SMS Transactions

**Base URL:** `http://localhost:8000`
**Format:** JSON
**Authentication:** HTTP Basic Auth is required on **every** endpoint.

| Username | Password |
|---|---|
| `admin` | `momo2024` |

With curl: `curl -u admin:momo2024 ...`
In Postman: **Authorization → Basic Auth**.
The header sent is `Authorization: Basic YWRtaW46bW9tbzIwMjQ=` (base64 of `admin:momo2024`).

---

## Transaction fields

Each transaction is produced by the XML parser (`dsa/parse_xml.py`) from one SMS in `modified_sms_v2.xml` (1,691 records).

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique id (1–1691 for the original records; new records get the next number) |
| `transaction_id` | string / null | MoMo Financial Transaction Id from the SMS |
| `type` | string | Transaction type, e.g. `incoming`, `payment` |
| `amount` | number | Amount in RWF |
| `sender` | string / null | Who sent the money |
| `receiver` | string / null | Who received the money |
| `fee` | number | Fee charged in RWF |
| `balance_after` | number / null | Account balance after the transaction |
| `timestamp` | string | Date and time the SMS was received, e.g. `10 May 2024 4:30:58 PM` |
| `date_ms` | string | Same time as Unix epoch milliseconds |
| `address` | string | SMS sender (`M-Money`) |
| `body` | string | Original SMS text |

---

## 1. GET /transactions — list all transactions

| | |
|---|---|
| **Method** | GET |
| **Endpoint** | `/transactions` |
| **Auth** | Required |

**Request example**
```bash
curl -u admin:momo2024 http://localhost:8000/transactions
```

**Response — 200 OK** (a JSON list of all 1,691 transactions; first one shown)
```json
[
  {
    "id": 1,
    "transaction_id": "76662021700",
    "type": "incoming",
    "amount": 2000,
    "sender": "Jane Smith",
    "receiver": null,
    "fee": 0,
    "balance_after": 2000,
    "timestamp": "10 May 2024 4:30:58 PM",
    "date_ms": "1715351458724",
    "address": "M-Money",
    "body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700."
  },
  ...
]
```

**Error codes:** `401` (missing or wrong credentials)

---

## 2. GET /transactions/{id} — get one transaction

| | |
|---|---|
| **Method** | GET |
| **Endpoint** | `/transactions/{id}` |
| **Auth** | Required |

**Request example**
```bash
curl -u admin:momo2024 http://localhost:8000/transactions/1
```

**Response — 200 OK**
```json
{
  "id": 1,
  "transaction_id": "76662021700",
  "type": "incoming",
  "amount": 2000,
  "sender": "Jane Smith",
  "receiver": null,
  "fee": 0,
  "balance_after": 2000,
  "timestamp": "10 May 2024 4:30:58 PM",
  "date_ms": "1715351458724",
  "address": "M-Money",
  "body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700."
}
```

**Error responses**

| Code | When | Body |
|---|---|---|
| 400 | id is not a number (e.g. `/transactions/abc`) | `{"error": "Invalid ID"}` |
| 401 | Missing or wrong credentials | `{"error": "Unauthorized"}` |
| 404 | No transaction with that id | `{"error": "Transaction not found"}` |

---

## 3. POST /transactions — add a transaction

| | |
|---|---|
| **Method** | POST |
| **Endpoint** | `/transactions` |
| **Auth** | Required |
| **Header** | `Content-Type: application/json` |

The server assigns the `id` automatically.

**Request example**
```bash
curl -u admin:momo2024 -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","amount":5000,"sender":"self","receiver":"Jane Smith","fee":100,"balance_after":3000,"timestamp":"2024-05-10 10:00:00"}'
```

**Response — 201 Created**
```json
{
  "type": "payment",
  "amount": 5000,
  "sender": "self",
  "receiver": "Jane Smith",
  "fee": 100,
  "balance_after": 3000,
  "timestamp": "2024-05-10 10:00:00",
  "id": 1692
}
```

**Error responses**

| Code | When | Body |
|---|---|---|
| 400 | Body is not valid JSON | `{"error": "Invalid JSON"}` |
| 401 | Missing or wrong credentials | `{"error": "Unauthorized"}` |

---

## 4. PUT /transactions/{id} — update a transaction

| | |
|---|---|
| **Method** | PUT |
| **Endpoint** | `/transactions/{id}` |
| **Auth** | Required |
| **Header** | `Content-Type: application/json` |

Only the fields you send are changed; all other fields keep their values.

**Request example**
```bash
curl -u admin:momo2024 -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount":9999}'
```

**Response — 200 OK** (the full updated transaction)
```json
{
  "id": 1,
  "transaction_id": "76662021700",
  "type": "incoming",
  "amount": 9999,
  "sender": "Jane Smith",
  "...": "other fields unchanged"
}
```

**Error responses**

| Code | When | Body |
|---|---|---|
| 400 | id is not a number, or body is not valid JSON | `{"error": "Invalid ID"}` / `{"error": "Invalid JSON"}` |
| 401 | Missing or wrong credentials | `{"error": "Unauthorized"}` |
| 404 | No transaction with that id | `{"error": "Transaction not found"}` |

---

## 5. DELETE /transactions/{id} — delete a transaction

| | |
|---|---|
| **Method** | DELETE |
| **Endpoint** | `/transactions/{id}` |
| **Auth** | Required |

**Request example**
```bash
curl -u admin:momo2024 -X DELETE http://localhost:8000/transactions/1
```

**Response — 200 OK**
```json
{ "message": "Transaction 1 deleted" }
```

**Error responses**

| Code | When | Body |
|---|---|---|
| 400 | id is not a number | `{"error": "Invalid ID"}` |
| 401 | Missing or wrong credentials | `{"error": "Unauthorized"}` |
| 404 | No transaction with that id | `{"error": "Transaction not found"}` |

---

## Authentication errors — 401 Unauthorized

Sent when the `Authorization` header is missing, is not Basic, or has the wrong username/password. The request is **not** carried out.

```bash
curl -i -u admin:wrongpassword http://localhost:8000/transactions
```
```http
HTTP/1.0 401 Unauthorized
WWW-Authenticate: Basic realm="MoMo API"
Content-Type: application/json

{"error": "Unauthorized"}
```

---

## Error code summary

| Code | Meaning |
|---|---|
| 200 OK | Request succeeded (GET, PUT, DELETE) |
| 201 Created | New transaction added (POST) |
| 400 Bad Request | Invalid id or malformed JSON |
| 401 Unauthorized | Missing or wrong credentials |
| 404 Not Found | Transaction id or URL path does not exist |

> **Note:** the server keeps transactions in memory. Changes made with POST, PUT and DELETE
> are lost when the server restarts, and it reloads the original 1,691 records.
