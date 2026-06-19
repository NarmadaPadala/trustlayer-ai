import json


def normalize_order(payload):
    data = json.loads(payload)
    return {
        "id": data["id"],
        "amount": float(data["amount"]),
        "currency": data.get("currency", "USD"),
    }

