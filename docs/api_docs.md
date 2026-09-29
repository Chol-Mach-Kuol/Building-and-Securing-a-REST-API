# MoMo SMS Transactions API

This API gives you access to the 1,691 mobile money transactions we parsed from `modified_sms_v2.xml`. You can list them, look one up, add new ones, edit them and delete them.

Start the server from the repository root:

```bash
python3 -m api.server
```

(On Windows, use `python -m api.server`.) You should see:

```
Loaded 1691 transactions
Server running on http://localhost:8000  (Ctrl+C to stop)
```

Everything goes in and comes out as JSON.

## Logging in

Every request needs Basic Authentication. If you leave it out or get the password wrong, you get a `401 Unauthorized` and nothing happens to the data.

- **Username:** `admin`
- **Password:** `momo2024`

With curl, add `-u admin:momo2024` to your command. In Postman, open the **Authorization** tab, pick **Basic Auth** and type the username and password.

Behind the scenes, the client sends this header:

```
Authorization: Basic YWRtaW46bW9tbzIwMjQ=
```

That long string is just `admin:momo2024` in base64. It isn't encrypted, and anyone who sees it can decode it, which is why Basic Auth should only be used over HTTPS in a real system.

## What a transaction looks like

Here's the first record in the dataset, exactly as the API returns it:

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

A few notes on the fields:

- `id` is our own number for each record (1 to 1691). The original SMS file didn't have one, so the parser assigns them in order.
- `transaction_id` is the Financial Transaction Id that MoMo put in the SMS, when there is one.
- `type` tells you what kind of transaction it was, for example `incoming` or `payment`.
- `amount`, `fee` and `balance_after` are in Rwandan francs (RWF).
- `sender` or `receiver` can be `null` when the SMS doesn't mention them.
- `timestamp` is when the phone received the SMS; `date_ms` is the same moment in milliseconds.
- `body` is the original SMS text, kept so you can always check where a value came from.

---

## Get all transactions

**`GET /transactions`**

Returns every transaction as a list.

```bash
curl -u admin:momo2024 http://localhost:8000/transactions
```

You'll get `200 OK` and a long JSON list, 1,691 items in total:

```json
[
  {
    "id": 1,
    "transaction_id": "76662021700",
    "type": "incoming",
    "amount": 2000,
    "sender": "Jane Smith",
    ...
  },
  ...
]
```

**Possible errors:** `401` if the credentials are missing or wrong.

---

## Get one transaction

**`GET /transactions/{id}`**

Returns a single transaction by its id.

```bash
curl -u admin:momo2024 http://localhost:8000/transactions/1
```

If it exists, you get `200 OK` and the transaction (it looks like the example above).

**If something goes wrong:**

- Asking for an id that doesn't exist, like `/transactions/99999`, gives `404`:
```json
  { "error": "Transaction 99999 not found" }
```
- Using something that isn't a number, like `/transactions/abc`, gives `400`:
```json
  { "error": "Transaction id must be a number" }
```
- Missing or wrong credentials give `401`.

---

## Add a transaction

**`POST /transactions`**

Send the new transaction as JSON in the request body. Don't include an `id`; the server picks the next free number for you.

```bash
curl -i -u admin:momo2024 -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","amount":5000,"sender":"self","receiver":"Jane Smith","fee":100,"balance_after":3000,"timestamp":"2024-05-10 10:00:00"}'
```

You get `201 Created`. The response includes a `Location` header pointing to the new record, and the body is the saved transaction with its new `id`:

```
HTTP/1.0 201 Created
Content-Type: application/json
Location: /transactions/1692
```

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

**If something goes wrong:**

- A body that isn't valid JSON gives `400`:
```json
  { "error": "Invalid JSON in request body" }
```
- Sending a POST to a single record, like `/transactions/5`, gives `405`:
```json
  { "error": "Use POST /transactions to create" }
```
- Missing or wrong credentials give `401`.

---

## Update a transaction

**`PUT /transactions/{id}`**

Send only the fields you want to change. Everything else stays as it was.

```bash
curl -u admin:momo2024 -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount":9999}'
```

You get `200 OK` and the full, updated transaction. Only `amount` has changed:

```json
{
  "id": 1,
  "transaction_id": "76662021700",
  "type": "incoming",
  "amount": 9999,
  "sender": "Jane Smith",
  ...
}
```

**If something goes wrong:**

- An id that doesn't exist gives `404`, e.g. `{ "error": "Transaction 99999 not found" }`.
- An id that isn't a number gives `400` with `{ "error": "Transaction id must be a number" }`.
- A body that isn't valid JSON gives `400` with `{ "error": "Invalid JSON in request body" }`.
- Sending a PUT to `/transactions` (with no id) gives `405` with `{ "error": "Use PUT /transactions/{id} to update" }`.
- Missing or wrong credentials give `401`.

---

## Delete a transaction

**`DELETE /transactions/{id}`**

Removes a transaction.

```bash
curl -u admin:momo2024 -X DELETE http://localhost:8000/transactions/1
```

You get `200 OK`, a confirmation message, and a copy of the record that was removed:

```json
{
  "message": "Transaction 1 deleted",
  "deleted": {
    "id": 1,
    "transaction_id": "76662021700",
    "type": "incoming",
    "amount": 2000,
    "sender": "Jane Smith",
    ...
  }
}
```

**If something goes wrong:**

- An id that doesn't exist (including one you already deleted) gives `404`, e.g. `{ "error": "Transaction 1 not found" }`.
- An id that isn't a number gives `400` with `{ "error": "Transaction id must be a number" }`.
- Sending a DELETE to `/transactions` (with no id) gives `405` with `{ "error": "Use DELETE /transactions/{id} to delete" }`.
- Missing or wrong credentials give `401`.

---

## When authentication fails

This is what a request with the wrong password looks like. The `-i` flag makes curl show the headers too:

```bash
curl -i -u admin:wrongpassword http://localhost:8000/transactions/1
```

```
HTTP/1.0 401 Unauthorized
WWW-Authenticate: Basic realm="MoMo API"
Content-Type: application/json
```

The `401` status and the `WWW-Authenticate` header tell the client it needs to log in with Basic Auth. You get the same response if you send no credentials at all, and the request is not carried out.

---

## Other errors

- A URL that isn't one of the endpoints above, like `/users`, gives `404`:
```json
  { "error": "Endpoint not found" }
```

---

## Status codes at a glance

| Code | What it means here |
|---|---|
| 200 OK | The request worked (GET, PUT, DELETE) |
| 201 Created | A new transaction was added (POST) |
| 400 Bad Request | The id isn't a number, or the JSON body is broken |
| 401 Unauthorized | Credentials are missing or wrong |
| 404 Not Found | That transaction, or that URL, doesn't exist |
| 405 Method Not Allowed | The method doesn't fit the URL (e.g. PUT without an id) |
