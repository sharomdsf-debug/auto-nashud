import requests
import re
import json
import subprocess
from datetime import datetime

# =========================
# BANKS
# =========================

banks = [
    {
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "url": "https://nbt.tj/tj/kurs/kurs.php"
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

def empty_currency():
    return {
        "buy": "0.0000",
        "sell": "0.0000"
    }

# =========================
# EXTRACT RATE
# =========================

def extract_currency(text, code):

    pattern = rf"{code}[^\d]*(\d+\.\d+)[^\d]+(\d+\.\d+)"

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        return {
            "buy": match.group(1),
            "sell": match.group(2)
        }

    return empty_currency()

# =========================
# CLEAN TEXT
# =========================

def clean_text(text):
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    return text

# =========================
# LOAD WEBSITE
# =========================

def load_text(url):

    try:

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        return response.text

    except Exception as e:

        print("LOAD ERROR:", e)

        return ""

# =========================
# MAIN
# =========================

rates = []

for bank in banks:

    print("\n======================")
    print("Checking:", bank["url"])

    html = load_text(bank["url"])

    text = clean_text(html)

    print("TEXT LOADED")

    currencies = {
        "USD": extract_currency(text, "USD"),
        "EUR": extract_currency(text, "EUR"),
        "RUB": extract_currency(text, "RUB"),
        "CNY": extract_currency(text, "CNY"),
        "KZT": extract_currency(text, "KZT")
    }

    rates.append({
        "bank_name": bank["name"],
        "bank_id": bank["id"],
        "currencies": currencies
    })

# =========================
# FINAL JSON
# =========================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": datetime.now().strftime("🔹%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": rates
}

# =========================
# PRINT
# =========================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

# =========================
# SAVE data.json
# =========================

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

print("\ndata.json saved")

# =========================
# GITHUB PUSH
# =========================

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

    subprocess.run(["git", "add", "data.json"])

    subprocess.run([
        "git",
        "commit",
        "-m",
        "Update exchange rates"
    ])

    subprocess.run(["git", "push"])

    print("\nGITHUB PUSH SUCCESS")

except Exception as e:

    print("\nGITHUB PUSH ERROR")
    print(e)
