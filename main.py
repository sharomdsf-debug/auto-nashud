import requests
import os
import re
import json
from datetime import datetime

# =========================
# FIRECRAWL API
# =========================

API_KEY = os.getenv("FIRECRAWL_API")

# =========================
# BANKS
# =========================

banks = [
    {
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "url": "https://nbt.tj/"
    },
    {
        "name": "Душанбе Сити Бонк",
        "id": "dushanbe_city",
        "url": "https://dc.tj/"
    },
    {
        "name": "Тавҳидбонк",
        "id": "tawhidbank",
        "url": "https://www.tawhidbank.tj/"
    }
]

# =========================
# DEFAULT CURRENCIES
# =========================

default_currencies = {
    "USD": {"buy": "0.0000", "sell": "0.0000"},
    "EUR": {"buy": "0.0000", "sell": "0.0000"},
    "RUB": {"buy": "0.0000", "sell": "0.0000"},
    "CNY": {"buy": "0.0000", "sell": "0.0000"},
    "KZT": {"buy": "0.0000", "sell": "0.0000"}
}

# =========================
# FINAL JSON
# =========================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": f"🔹{datetime.now().strftime('%d.%m.%Y %H:%M')}",
    "base_currency": "TJS",
    "status": "success",
    "rates": []
}

# =========================
# FUNCTION
# =========================

def find_currency(text, currency):

    pattern = rf"{currency}\s+([0-9.]+)\s+([0-9.]+)"

    match = re.search(pattern, text)

    if match:
        return {
            "buy": match.group(1),
            "sell": match.group(2)
        }

    return {
        "buy": "0.0000",
        "sell": "0.0000"
    }

# =========================
# LOOP BANKS
# =========================

for bank in banks:

    print("\n====================")
    print("Checking:", bank["url"])

    try:

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "url": bank["url"],
                "formats": ["markdown"],
                "waitFor": 10000
            },
            timeout=120
        )

        data = response.json()

        if "data" not in data:
            print("SCRAPE ERROR")
            continue

        text = data["data"]["markdown"]

        print("TEXT LOADED")

        currencies = default_currencies.copy()

        # =========================
        # PARSE
        # =========================

        currencies["USD"] = find_currency(text, "USD")
        currencies["EUR"] = find_currency(text, "EUR")
        currencies["RUB"] = find_currency(text, "RUB")
        currencies["CNY"] = find_currency(text, "CNY")
        currencies["KZT"] = find_currency(text, "KZT")

        # =========================
        # APPEND
        # =========================

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": currencies
        })

    except Exception as e:

        print("ERROR:")
        print(str(e))

# =========================
# SAVE JSON
# =========================

with open("rates.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

# =========================
# PRINT
# =========================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))
