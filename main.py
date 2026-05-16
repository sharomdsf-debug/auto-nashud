import requests
import os
import json
from datetime import datetime

# ======================================
# API KEYS
# ======================================

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
OPENROUTER_API = os.getenv("OPENROUTER_API")

# ======================================
# BANKS
# ======================================

banks = [
    {
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "website": "https://nbt.tj"
    },
    {
        "name": "Амонатбонк",
        "id": "amonatbonk",
        "website": "https://amonatbonk.tj"
    },
    {
        "name": "Ориёнбонк",
        "id": "oriyonbank",
        "website": "https://oriyonbonk.tj"
    },
    {
        "name": "Тавҳидбонк",
        "id": "tawhid",
        "website": "https://www.tawhidbank.tj"
    },
    {
        "name": "Бонки Эсхата",
        "id": "eskhata",
        "website": "https://eskhata.com"
    },
    {
        "name": "Коммерсбонк",
        "id": "commerce",
        "website": "https://cbt.tj"
    },
    {
        "name": "Тиҷорат Бонк",
        "id": "tijorat",
        "website": "https://tijoratbank.tj"
    },
    {
        "name": "Спитамен Бонк",
        "id": "spitamen",
        "website": "https://spitamenbank.tj"
    },
    {
        "name": "Имон Интернешнл Банк",
        "id": "imon",
        "website": "https://imon.tj"
    },
    {
        "name": "Душанбе Сити",
        "id": "dushanbe_city",
        "website": "https://dc.tj"
    },
    {
        "name": "Алиф Бонк",
        "id": "alif",
        "website": "https://alif.tj"
    },
    {
        "name": "Саноатсодиротбонк",
        "id": "ssb",
        "website": "https://ssb.tj"
    },
    {
        "name": "IBT",
        "id": "ibt",
        "website": "https://ibt.tj"
    },
    {
        "name": "ICB",
        "id": "icb",
        "website": "https://icb.tj"
    },
    {
        "name": "Микрофинансбонк",
        "id": "mfb",
        "website": "https://mfb.tj"
    },
    {
        "name": "Бонки рушди Тоҷикистон",
        "id": "sdb",
        "website": "https://brt.tj"
    },
    {
        "name": "Ҳумо",
        "id": "humo",
        "website": "https://humo.tj"
    },
    {
        "name": "Арванд",
        "id": "arvand",
        "website": "https://arvand.tj"
    },
    {
        "name": "FINCA",
        "id": "finca",
        "website": "https://finca.tj"
    },
    {
        "name": "Фридом Бонк Тоҷикистон",
        "id": "freedom",
        "website": "https://freedombank.tj"
    },
    {
        "name": "Васл Бонк",
        "id": "vasl",
        "website": "https://vasl.tj"
    },
    {
        "name": "Актив Бонк",
        "id": "aktiv",
        "website": "https://aktivbank.tj"
    },
    {
        "name": "Азизи-Молия",
        "id": "azizi",
        "website": "https://azizimoliya.tj"
    },
    {
        "name": "Матин",
        "id": "matin",
        "website": "https://matin.tj"
    }
]

# ======================================
# DEFAULT CURRENCIES
# ======================================

EMPTY_CURRENCIES = {
    "USD": {"buy": "0.0000", "sell": "0.0000"},
    "EUR": {"buy": "0.0000", "sell": "0.0000"},
    "RUB": {"buy": "0.0000", "sell": "0.0000"},
    "CNY": {"buy": "0.0000", "sell": "0.0000"},
    "KZT": {"buy": "0.0000", "sell": "0.0000"}
}

# ======================================
# FINAL JSON
# ======================================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": []
}

# ======================================
# LOOP BANKS
# ======================================

for bank in banks:

    print("\n============================")
    print("Checking:", bank["website"])

    try:

        # ======================================
        # FIRECRAWL
        # ======================================

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API}",
                "Content-Type": "application/json"
            },
            json={
                "url": bank["website"],
                "formats": ["markdown"],
                "waitFor": 300000
            },
            timeout=300
        )

        data = response.json()

        if "data" not in data:

            print("NO DATA")

            final_json["rates"].append({
                "bank_name": bank["name"],
                "bank_id": bank["id"],
                "currencies": EMPTY_CURRENCIES
            })

            continue

        markdown = data["data"].get("markdown", "")

        if not markdown:

            print("NO MARKDOWN")

            final_json["rates"].append({
                "bank_name": bank["name"],
                "bank_id": bank["id"],
                "currencies": EMPTY_CURRENCIES
            })

            continue

        print("TEXT LOADED")

        # ======================================
        # PROMPT
        # ======================================

        prompt = f"""
You are an AI banking exchange-rate extraction system.

Extract ONLY currency exchange rates from the markdown.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

VERY IMPORTANT RULES:

1. Return ONLY valid JSON.
2. No markdown.
3. No explanation.
4. No comments.
5. No text before JSON.
6. No text after JSON.
7. Never invent values.
8. If currency missing:
buy = "0.0000"
sell = "0.0000"

9. If ONLY ONE rate exists:
use:
"buy" = existing rate
"sell" = "0.0000"

10. JSON MUST match EXACTLY this structure:

{{
  "bank_name": "{bank['name']}",
  "bank_id": "{bank['id']}",
  "currencies": {{
    "USD": {{"buy":"0.0000","sell":"0.0000"}},
    "EUR": {{"buy":"0.0000","sell":"0.0000"}},
    "RUB": {{"buy":"0.0000","sell":"0.0000"}},
    "CNY": {{"buy":"0.0000","sell":"0.0000"}},
    "KZT": {{"buy":"0.0000","sell":"0.0000"}}
  }}
}}

MARKDOWN:
{markdown[:30000]}
"""

        # ======================================
        # AI REQUEST
        # ======================================

        ai_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-v4-flash:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=60
        )

        ai_data = ai_response.json()

        print("\n========== AI RESPONSE ==========")
        print(json.dumps(ai_data, ensure_ascii=False, indent=2))

        content = ai_data["choices"][0]["message"]["content"]

        parsed = json.loads(content)

        final_json["rates"].append(parsed)

        print("BANK ADDED")

    except Exception as e:

        print("ERROR:", str(e))

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": EMPTY_CURRENCIES
        })

# ======================================
# SAVE JSON
# ======================================

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

print("\n========== FINAL JSON ==========")
print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\nDATA SAVED TO data.json")
