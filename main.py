import requests
import os
import json
from datetime import datetime

# ==========================================
# API KEYS
# ==========================================

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
OPENROUTER_API = os.getenv("OPENROUTER_API")

# ==========================================
# BANKS
# ==========================================

banks = [
    {
        "name": "Тавҳидбонк",
        "id": "tawhidbank",
        "website": "https://www.tawhidbank.tj",
        "url": "https://www.tawhidbank.tj/"
    },
    {
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "website": "https://nbt.tj",
        "url": "https://nbt.tj/"
    },
    {
        "name": "Амонатбонк",
        "id": "amonatbonk",
        "website": "https://amonatbonk.tj",
        "url": "https://amonatbonk.tj/"
    }
]

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
# LOOP BANKS
# ==========================================

for bank in banks:

    print("\n========================")
    print("Checking:", bank["url"])

    # ==========================================
    # FIRECRAWL SCRAPE
    # ==========================================

    try:

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API}",
                "Content-Type": "application/json"
            },
            json={
                "url": bank["url"],
                "formats": ["markdown"],
                "waitFor": 10000
            },
            timeout=30
        )

        data = response.json()

    except Exception as e:

        print("FIRECRAWL ERROR")
        print(e)

        continue

    # ==========================================
    # CHECK MARKDOWN
    # ==========================================

    if "data" not in data or "markdown" not in data["data"]:

        print("SCRAPE FAILED")
        print(data)

        continue

    markdown_text = data["data"]["markdown"]

    print("TEXT LOADED")

    # ==========================================
    # AI PROMPT
    # ==========================================

    prompt = f"""
Аз ҳамин markdown қурби асъорро ёб.

Танҳо ҳамин асъорҳоро гир:

USD
EUR
RUB
CNY
KZT

Агар асъор ёфт нашавад:
buy ва sell = 0.0000

Фақат JSON баргардон.

Формат:

{{
  "bank_name": "{bank["name"]}",
  "bank_id": "{bank["id"]}",
  "website": "{bank["website"]}",
  "currencies": {{
    "USD": {{ "buy": "", "sell": "" }},
    "EUR": {{ "buy": "", "sell": "" }},
    "RUB": {{ "buy": "", "sell": "" }},
    "CNY": {{ "buy": "", "sell": "" }},
    "KZT": {{ "buy": "", "sell": "" }}
  }}
}}

MARKDOWN:
{markdown_text[:15000]}
"""

    # ==========================================
    # AI REQUEST
    # ==========================================

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
                        "role": "system",
                        "content": "Фақат JSON баргардон."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=30
        )

        result = ai_response.json()

    except Exception as e:

        print("AI REQUEST ERROR")
        print(e)

        continue

    # ==========================================
    # PRINT RAW AI RESPONSE
    # ==========================================

    print("\n========== AI RESPONSE ==========\n")

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # ==========================================
    # PARSE AI JSON
    # ==========================================

    try:

        content = result["choices"][0]["message"]["content"]

        parsed = json.loads(content)

        final_json["rates"].append(parsed)

        print("BANK ADDED")

    except Exception as e:

        print("AI JSON ERROR")
        print(e)

# ==========================================
# SAVE JSON FILE
# ==========================================

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==========================================
# PRINT FINAL JSON
# ==========================================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))
