import requests
import os
import json
from datetime import datetime

# ==============================
# API KEYS
# ==============================

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
OPENROUTER_API = os.getenv("OPENROUTER_API")

# ==============================
# BANKS
# ==============================

banks = [
    {
        "name": "Тавҳидбонк",
        "id": "tawhidbank",
        "website": "https://www.tawhidbank.tj/"
    },
    {
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "website": "https://nbt.tj/"
    },
    {
        "name": "Амонатбонк",
        "id": "amonatbonk",
        "website": "https://amonatbonk.tj/"
    }
]

# ==============================
# FINAL JSON
# ==============================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": []
}

# ==============================
# LOOP
# ==============================

for bank in banks:

    print("\n============================")
    print("Checking:", bank["website"])

    # ==========================
    # FIRECRAWL SCRAPE
    # ==========================

    try:

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API}",
                "Content-Type": "application/json"
            },
            json={
                "url": bank["website"],
                "formats": ["markdown"],
                "waitFor": 10000
            },
            timeout=30
        )

        data = response.json()

    except Exception as e:
        print("FIRECRAWL ERROR:", e)
        continue

    # ==========================
    # GET MARKDOWN
    # ==========================

    markdown = ""

    if "data" in data and "markdown" in data["data"]:
        markdown = data["data"]["markdown"]
        print("TEXT LOADED")
    else:
        print("NO MARKDOWN")
        continue

    # ==========================
    # AI PROMPT
    # ==========================

    prompt = f"""
You are a currency extraction AI.

Extract ONLY currency exchange rates from this text.

Currencies:
USD
EUR
RUB
CNY
KZT

Rules:
- Return ONLY JSON
- No markdown
- No explanation
- If currency missing use:
"0.0000"

FORMAT:

{{
  "USD": {{"buy":"0.0000","sell":"0.0000"}},
  "EUR": {{"buy":"0.0000","sell":"0.0000"}},
  "RUB": {{"buy":"0.0000","sell":"0.0000"}},
  "CNY": {{"buy":"0.0000","sell":"0.0000"}},
  "KZT": {{"buy":"0.0000","sell":"0.0000"}}
}}

TEXT:

{markdown[:12000]}
"""

    # ==========================
    # OPENROUTER AI
    # ==========================

    try:

        ai_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=30
        )

        ai_data = ai_response.json()

        print("\n========== AI RESPONSE ==========\n")
        print(ai_data)

        content = ai_data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        continue

    # ==========================
    # PARSE JSON
    # ==========================

    try:

        currencies = json.loads(content)

    except Exception as e:

        print("JSON ERROR:", e)
        continue

    # ==========================
    # ADD BANK
    # ==========================

    final_json["rates"].append({
        "bank_name": bank["name"],
        "bank_id": bank["id"],
        "website": bank["website"],
        "currencies": currencies
    })

# ==============================
# SAVE JSON
# ==============================

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==============================
# PRINT
# ==============================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\nDATA SAVED TO data.json")
