# Building and Securing a REST API

A REST API built in plain Python (`http.server`) that serves MTN MoMo SMS transaction data parsed from an XML file. Includes Basic Authentication, DSA search comparison, and full API documentation.

## Team

| Member | Role |
|--------|------|
| Chol Mach | Team Lead + Data Parsing |
| Kuol Akech | API Implementation |
| Abay Tessema | Authentication & Security |
| Alier Akuang | DSA + Documentation + Testing |

---

## Project Structure

```
Building-and-Securing-a-REST-API/
├── api/
│   ├── server.py          # REST API server (CRUD endpoints)
│   └── auth.py            # Basic Authentication middleware
├── dsa/
│   ├── parse_xml.py       # XML parser → JSON
│   └── search.py          # Linear search vs dictionary lookup
├── docs/
│   └── api_docs.md        # Full API documentation
├── screenshots/           # Test evidence (curl/Postman)
├── modified_sms_v2.xml    # Source data
├── README.md
└── COLLABORATION.md       # Team task division guide
```

---

## Requirements

- Python 3.8+
- No external dependencies — uses only the Python standard library

---

## Setup

```bash
git clone https://github.com/Chol-Mach-Kuol/Building-and-Securing-a-REST-API.git
cd Building-and-Securing-a-REST-API
```

---

## Running the API Server

```bash
python api/server.py
```

The server starts on `http://localhost:8000`.

---

## Running the XML Parser

```bash
python dsa/parse_xml.py
```

Outputs the total number of parsed transactions and a preview of the first 3 records.

---

## Running the DSA Search Comparison

```bash
python dsa/search.py
```

Prints a timing comparison between linear search and dictionary lookup over 20+ records.

---

## Authentication

All endpoints require Basic Authentication.

- **Username:** `admin`
- **Password:** `momo2024`

---

## Example curl Commands

**GET all transactions:**
```bash
curl -u admin:momo2024 http://localhost:8000/transactions
```

**GET single transaction:**
```bash
curl -u admin:momo2024 http://localhost:8000/transactions/1
```

**POST new transaction:**
```bash
curl -u admin:momo2024 -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","amount":5000,"sender":"self","receiver":"Jane Smith","fee":100,"balance_after":3000,"timestamp":"2024-05-10 10:00:00"}'
```

**PUT update transaction:**
```bash
curl -u admin:momo2024 -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount":9999}'
```

**DELETE transaction:**
```bash
curl -u admin:momo2024 -X DELETE http://localhost:8000/transactions/1
```

**Unauthorized request (wrong credentials):**
```bash
curl -u admin:wrongpassword http://localhost:8000/transactions
```

---

## API Documentation

See [docs/api_docs.md](docs/api_docs.md) for full endpoint documentation including request/response examples and error codes.
