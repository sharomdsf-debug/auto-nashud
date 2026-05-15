import requests
import json
import re

# FIRECRAWL API
FIRECRAWL_API = "fc-14ada6fed79d4c0f9c39ad1bf213aad3"

# WEBSITE
url = "https://www.tawhidbank.tj/"

print("\n====================")
print("Checking:", url)

# =========================
# FIRECRAWL SCRAPE
# =========================

response = requests.post(
    "https://api.firecrawl.dev/v1/scrape",
    headers={
        "Authorization": f"Bearer {FIRECRAWL_API}",
        "Content-Type": "application/json"
    },
    json={
        "url": url,
        "formats": ["markdown"],
        "waitFor": 10000
    },
    timeout=120
)

data = response.json()

# DEBUG
print("\n===== FIRECRAWL RESPONSE =====\n")
print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])

# CHECK
if "data" not in data:
    print("\nFIRECRAWL ERROR")
    exit()

# WEBSITE TEXT
text = data["data"]["markdown"]

print("\nTEXT LOADED")

# =========================
# REGEX
# =========================

usd = re.search(r'USD\\s+(\\d+\\.\\d+)\\s+(\\d+\\.\\d+)', text)
eur = re.search(r'EUR\\s+(\\d+\\.\\d+)\\s+(\\d+\\.\\d+)', text)
rub = re.search(r'RUB\\s+(\\d+\\.\\d+)\\s+(\\d+\\.\\d+)', text)

# =========================
# JSON RESULT
# =========================

result = {
    "usd_buy": usd.group(1) if usd else None,
    "usd_sell": usd.group(2) if usd else None,

    "eur_buy": eur.group(1) if eur else None,
    "eur_sell": eur.group(2) if eur else None,

    "rub_buy": rub.group(1) if rub else None,
    "rub_sell": rub.group(2) if rub else None
}

# =========================
# PRINT JSON
# =========================

print("\n===== FINAL JSON =====\n")

print(json.dumps(result, indent=2, ensure_ascii=False))
