import xml.etree.ElementTree as ET
import re
import json


def detect_transaction_type(body):
    body_lower = body.lower()
    if "you have received" in body_lower:
        return "incoming"
    elif "transferred to" in body_lower:
        return "transfer"
    elif "your payment of" in body_lower:
        return "payment"
    elif "bank deposit" in body_lower:
        return "deposit"
    elif "transaction of" in body_lower and "direct payment" in body_lower:
        return "debit"
    elif "airtime" in body_lower:
        return "airtime"
    else:
        return "unknown"


def extract_amount(body):
    match = re.search(r'(\d[\d,]*)\s*RWF', body)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def extract_sender(body):
    match = re.search(r'received\s+\d[\d,]*\s+RWF\s+from\s+([A-Za-z\s]+)\s*\(', body)
    if match:
        return match.group(1).strip()
    match = re.search(r'transferred to\s+([A-Za-z\s]+)\s*\(', body)
    if match:
        return "self"
    return None


def extract_receiver(body):
    match = re.search(r'transferred to\s+([A-Za-z\s]+)\s*\(', body)
    if match:
        return match.group(1).strip()
    match = re.search(r'payment of\s+[\d,]+\s+RWF\s+to\s+([A-Za-z\s]+)\s+\d+', body)
    if match:
        return match.group(1).strip()
    match = re.search(r'transaction of\s+[\d,]+\s+RWF\s+by\s+([A-Z\s]+)\s+on', body)
    if match:
        return match.group(1).strip()
    return None


def extract_transaction_id(body):
    match = re.search(r'(?:TxId[:\s]+|Financial Transaction Id[:\s]+|TxId:\s*)(\d+)', body)
    if match:
        return match.group(1)
    return None


def extract_fee(body):
    match = re.search(r'[Ff]ee was[:\s]+(\d[\d,]*)\s*RWF', body)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0


def extract_balance(body):
    match = re.search(r'[Nn]ew balance[:\s]+(\d[\d,]*)\s*RWF', body)
    if match:
        return int(match.group(1).replace(",", ""))
    match = re.search(r'NEW BALANCE\s*[:\s]+(\d[\d,]*)\s*RWF', body)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def parse_sms_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    transactions = []

    for idx, sms in enumerate(root.findall("sms"), start=1):
        body = sms.get("body", "")
        record = {
            "id": idx,
            "transaction_id": extract_transaction_id(body),
            "type": detect_transaction_type(body),
            "amount": extract_amount(body),
            "sender": extract_sender(body),
            "receiver": extract_receiver(body),
            "fee": extract_fee(body),
            "balance_after": extract_balance(body),
            "timestamp": sms.get("readable_date"),
            "date_ms": sms.get("date"),
            "address": sms.get("address"),
            "body": body,
        }
        transactions.append(record)

    return transactions


if __name__ == "__main__":
    import os
    xml_path = os.path.join(os.path.dirname(__file__), "..", "modified_sms_v2.xml")
    transactions = parse_sms_xml(xml_path)
    print(f"Parsed {len(transactions)} transactions.")
    print(json.dumps(transactions[:3], indent=2))
