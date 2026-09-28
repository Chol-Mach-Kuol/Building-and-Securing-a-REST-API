# Team Collaboration Guide — Building and Securing a REST API

## Team Structure (4 Members)

| Role | Member | GitHub Handle |
|------|--------|---------------|
| Team Lead | Chol Mach | @cholmach |
| Backend Dev | Kuol Akech | @kuolakech |
| Security & Auth | Abay Tessema | @abaytessema |
| DSA & Testing | Alier Akuang | @alierakuang |

> Update GitHub handles above before submission.

---

## Task Division

### Chol Mach — Team Lead + Data Parsing (Task 1 + Project Setup)
**Points coverage:** Data Parsing (5 pts) + repo coordination

**Responsibilities:**
- Create the GitHub repository and all required folders (`api/`, `dsa/`, `docs/`, `screenshots/`)
- Write `dsa/parse_xml.py` to:
  - Open and parse `modified_sms_v2.xml` using Python's `xml.etree.ElementTree`
  - Extract every SMS record with ALL key fields: transaction type, amount, sender, receiver, timestamp, and any other attributes present
  - Convert each record into a Python dictionary
  - Return the full list of dictionaries as JSON-compatible objects
  - Print or export the result so Kuol can load it in the API
- Write `README.md` with:
  - Project description
  - How to install dependencies (if any)
  - How to run the API server (`python api/server.py`)
  - How to run the DSA script (`python dsa/search.py`)
  - Example curl commands for testing
- Create and maintain the Scrum Board (GitHub Projects) — add all tasks as cards and assign to each member
- Fill out and maintain the team participation sheet (only the Team Lead edits it; others get comment-only access)
- Review and merge all Pull Requests into `main`

**Deliverables:**
- `dsa/parse_xml.py` — fully working XML parser outputting list of dicts
- `README.md` — complete setup and run instructions
- GitHub repo folder structure initialized
- Scrum Board set up with all task cards assigned

**Folder to own:** `dsa/parse_xml.py`

---

### Kuol Akech — API Implementation (Task 2)
**Points coverage:** API Implementation (5 pts)

**Responsibilities:**
- Build the REST API using **plain Python `http.server`** — no Flask, no FastAPI
- Import and use the parsed JSON data from `dsa/parse_xml.py` as the in-memory data store
- Implement all 5 CRUD endpoints with correct HTTP methods:
  - `GET /transactions` — return the full list of all SMS transactions as JSON
  - `GET /transactions/{id}` — return a single transaction by ID; return `404 Not Found` if ID does not exist
  - `POST /transactions` — accept a JSON body, add a new transaction, return `201 Created` with the new record
  - `PUT /transactions/{id}` — accept a JSON body, update an existing record by ID; return `404 Not Found` if ID does not exist
  - `DELETE /transactions/{id}` — remove a record by ID; return `404 Not Found` if ID does not exist, `200 OK` on success
- Set `Content-Type: application/json` on all responses
- Return correct HTTP status codes for every case: `200`, `201`, `400`, `404`
- Integrate Abay's `auth.py` so every endpoint is protected — call the auth check at the top of each handler
- Handle malformed JSON in POST/PUT bodies gracefully with `400 Bad Request`

**Deliverables:**
- `api/server.py` — fully working API server with all 5 endpoints
- All endpoints must work correctly before Abay adds auth on top

**Folder to own:** `api/server.py`

---

### Abay Tessema — Authentication & Security (Task 3)
**Points coverage:** Authentication & Security (5 pts)

**Responsibilities:**
- Write `api/auth.py` with a `check_auth(handler)` function that:
  - Reads the `Authorization` header from the request
  - Decodes the Base64-encoded `username:password`
  - Returns `True` if credentials match the expected values, `False` otherwise
- Integrate the auth check into Kuol's `api/server.py` so every endpoint calls `check_auth`
- When credentials are missing or wrong:
  - Return HTTP `401 Unauthorized`
  - Include the `WWW-Authenticate: Basic realm="MoMo API"` header in the response
  - Return a JSON body: `{"error": "Unauthorized"}`
- Test authentication using `curl`:
  - Valid credentials → successful response
  - Wrong password → `401` response
  - No credentials → `401` response
- Take screenshots of all three test cases above
- Write the security section of the PDF report covering:
  - How Basic Auth works (Base64 encoding, not encryption)
  - Why Basic Auth is weak: credentials sent in every request, Base64 is reversible, vulnerable without HTTPS, no token expiry
  - Stronger alternatives: **JWT** (JSON Web Tokens) — explain how it works and why it's better; **OAuth2** — explain the flow and use cases
  - Recommendation: always use HTTPS with any auth method

**Deliverables:**
- `api/auth.py` — Basic Auth logic
- `screenshots/auth_success.png` — valid credentials accepted
- `screenshots/auth_fail_wrong.png` — wrong credentials rejected with 401
- `screenshots/auth_fail_none.png` — no credentials rejected with 401
- Security section written for the PDF report

**Folder to own:** `api/auth.py` + `screenshots/` (auth screenshots)

---

### Alier Akuang — DSA Integration, Documentation & Testing (Tasks 4 + 5 + 6)
**Points coverage:** DSA Integration (5 pts) + API Documentation (5 pts)

**Responsibilities:**

**DSA (`dsa/search.py`):**
- Load the parsed transactions from `dsa/parse_xml.py` (use at least 20 records)
- Implement **Linear Search**: loop through the list to find a transaction by ID, measure time with Python's `time` module
- Implement **Dictionary Lookup**: build a `dict` of `{id: transaction}`, find by key, measure time with `time` module
- Run both methods on the same dataset and print a comparison table showing time taken for each
- Write a reflection (in comments or printed output) answering:
  - Why is dictionary lookup faster than linear search? (O(1) vs O(n))
  - Suggest at least one other data structure or algorithm that could improve search efficiency (e.g., binary search on a sorted list, hash map, B-tree) and explain why

**API Documentation (`docs/api_docs.md`):**
- Document every endpoint with:
  - Endpoint URL and HTTP method
  - Description of what it does
  - Authentication requirement
  - Request headers example
  - Request body example (for POST and PUT)
  - Successful response example with status code
  - Error response examples with status codes (401, 404, 400)
- Include a section on error codes table listing all possible codes and their meanings

**Testing & Validation:**
- Use `curl` or Postman to test every endpoint
- Take screenshots for:
  - `screenshots/get_all.png` — successful `GET /transactions` with valid auth
  - `screenshots/get_one.png` — successful `GET /transactions/{id}` with valid auth
  - `screenshots/post_test.png` — successful `POST /transactions`
  - `screenshots/put_test.png` — successful `PUT /transactions/{id}`
  - `screenshots/delete_test.png` — successful `DELETE /transactions/{id}`

**Deliverables:**
- `dsa/search.py` — linear search and dictionary lookup with timing and reflection
- `docs/api_docs.md` — complete API documentation
- All 5 test screenshots in `screenshots/`

**Folder to own:** `dsa/search.py` + `docs/` + `screenshots/` (test screenshots)

---

## Repository Structure

```
Building-and-Securing-a-REST-API/
├── api/
│   ├── server.py              ← Kuol Akech
│   └── auth.py                ← Abay Tessema
├── dsa/
│   ├── parse_xml.py           ← Chol Mach
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
├── modified_sms_v2.xml        ← shared input file
├── README.md                  ← Chol Mach
└── COLLABORATION.md           ← this file
```

---

## Git Workflow

1. Each member works on their own branch:
   - `feature/chol-parsing`
   - `feature/kuol-api`
   - `feature/abay-auth`
   - `feature/alier-dsa`
2. Open a Pull Request (PR) to `main` when your task is done.
3. Chol Mach (Team Lead) reviews and merges all PRs.
4. Commit messages must be descriptive: `Add XML parser for SMS records` not `update`.
5. Kuol should merge first, then Abay integrates auth on top, then Alier tests the final combined server.

---

## Scrum Board (GitHub Projects)

Create a GitHub Project board with these columns:

| To Do | In Progress | In Review | Done |
|-------|-------------|-----------|------|

Each task above becomes a card. Assign cards to the responsible member and move as work progresses. This is required for the Individual Effort Verification grade multiplier.

---

## Deadlines (internal — before Tuesday 11:59pm)

| Milestone | Owner | Internal Deadline |
|-----------|-------|-------------------|
| Repo setup + XML parser | Chol Mach | Day 1 |
| CRUD API endpoints | Kuol Akech | Day 3 |
| Basic Auth integrated + screenshots | Abay Tessema | Day 4 |
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

- Every member **must** have real commits in the GitHub repo — no commits = 0 multiplier on your individual grade regardless of team score.
- Screenshots must be real (taken from your own terminal/Postman), not copied from online.
- The team participation sheet is Chol Mach's responsibility — all sections must be fully completed.
- Other members are added to the participation sheet with **comment-only** access — do not edit it directly.
- If you are stuck, open a GitHub Issue and tag your teammate rather than going silent.
