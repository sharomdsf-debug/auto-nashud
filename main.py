import requests
import os
import json

FIRECRAWL_API = os.getenv("FIRECRAWL_API")

banks = [
    "https://www.tawhidbank.tj/"
]

for url in banks:

    print("\n====================")
    print("Checking:", url)

    # FIRECRAWL
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
        }
    )

    data = response.json()

    if "data" not in data:
        print("FIRECRAWL ERROR")
        print(data)
        continue

    website_text = data["data"]["markdown"]

    print("TEXT LOADED")

    # HUGGINGFACE
    ai_response = requests.post(
        "https://api-inference.huggingface.co/models/google/flan-t5-large",
        json={
            "inputs": f"""
Аз ин матн қурби USD EUR RUB-ро ёб
ва фақат JSON баргардон.

Формат:

{{
  "usd_buy": "",
  "usd_sell": "",
  "eur_buy": "",
  "eur_sell": "",
  "rub_buy": "",
  "rub_sell": ""
}}

Матн:

{website_text}
"""
        },
        timeout=120
    )

    print("\n===== HUGGINGFACE RAW RESPONSE =====\n")

    print(ai_response.text)
