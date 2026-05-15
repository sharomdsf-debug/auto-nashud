import requests
import os
import re
import json
import subprocess
from datetime import datetime

# ==========================================
# FIRECRAWL API
# ==========================================

API_KEY = os.getenv("FIRECRAWL_API")

# ==========================================
# BANKS
# ==========================================

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

# ==========================================
# DEFAULT CURRENCIES
# ==========================================

default_currencies = {
    "USD": {"buy": "0.0000", "sell": "0.0000"},
    "EUR": {"buy": "0.0000", "sell": "0.0000"},
    "RUB": {"buy": "0.0000", "sell": "0.0000"},
    "CNY": {"buy": "0.0000", "sell": "0.0000"},
    "KZT": {"buy": "0.0000", "sell": "0.0000"}
}

# ==========================================
# FINAL JSON
# ==========================================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": f"🔹{datetime.now().strftime('%d.%m.%Y %H:%M')}",
    "base_currency": "TJS",
    "status": "success",
    "rates": []
}

# ==========================================
# FIND CURRENCY
# ==========================================

def find_currency(text, currency):

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned.append(line)

    lines = cleaned

    currency_aliases = {
        "USD": [
            "USD",
            "USDTJS",
            "USD/TJS",
            "$",
            "ДОЛЛАР",
            "ДОЛЛАРИ ИМА",
            "ДОЛЛАР США"
        ],
        "EUR": [
            "EUR",
            "EURTJS",
            "EUR/TJS",
            "€",
            "ЕВРО"
        ],
        "RUB": [
            "RUB",
            "RUB/TJS",
            "RUBTJS",
            "РУБ",
            "РУБЛ",
            "РУБЛЬ"
        ],
        "CNY": [
            "CNY",
            "CNY/TJS",
            "ЮАН",
            "YUAN"
        ],
        "KZT": [
            "KZT",
            "KZT/TJS",
            "ТЕНГЕ",
            "КАЗАХСТОН"
        ]
    }

    aliases = currency_aliases.get(currency, [currency])

    for i, line in enumerate(lines):

        upper_line = line.upper()

        found = False

        for alias in aliases:

            if alias.upper() in upper_line:
                found = True
                break

        if not found:
            continue

        nearby = " ".join(lines[i:i+10])

        numbers = re.findall(r"\d+[.,]\d+", nearby)

        numbers = [n.replace(",", ".") for n in numbers]

        filtered = []

        for n in numbers:

            try:

                value = float(n)

                if 0.0001 <= value <= 1000:
                    filtered.append(f"{value:.4f}")

            except:
                pass

        if len(filtered) >= 2:

            return {
                "buy": filtered[0],
                "sell": filtered[1]
            }

        elif len(filtered) == 1:

            return {
                "buy": filtered[0],
                "sell": "0.0000"
            }

    return {
        "buy": "0.0000",
        "sell": "0.0000"
    }

# ==========================================
# SCRAPE BANKS
# ==========================================

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

        currencies = {
            "USD": find_currency(text, "USD"),
            "EUR": find_currency(text, "EUR"),
            "RUB": find_currency(text, "RUB"),
            "CNY": find_currency(text, "CNY"),
            "KZT": find_currency(text, "KZT")
        }

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": currencies
        })

    except Exception as e:

        print("ERROR:")
        print(str(e))

# ==========================================
# SAVE JSON
# ==========================================

with open("rates.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==========================================
# PRINT RESULT
# ==========================================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

# ==========================================
# GITHUB AUTO PUSH
# ==========================================

try:

    subprocess.run([
        "git",
        "config",
        "--global",
        "user.name",
        "github-actions"
    ])

    subprocess.run([
        "git",
        "config",
        "--global",
        "user.email",
        "github-actions@github.com"
    ])

    subprocess.run(["git", "add", "rates.json"])

    subprocess.run([
        "git",
        "commit",
        "-m",
        "update exchange rates"
    ])

    subprocess.run(["git", "push"])

    print("\nGITHUB PUSH SUCCESS")

except Exception as e:

    print("\nGITHUB PUSH ERROR")
    print(str(e))
