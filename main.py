import requests
import os
import json
import time
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
        "name": "Бонки Миллии Тоҷикистон",
        "id": "nbt",
        "website": "https://nbt.tj/"
    },
    {
        "name": "Амонатбонк",
        "id": "amonatbonk",
        "website": "https://amonatbonk.tj/"
    },
    {
        "name": "Ориёнбонк",
        "id": "oriyonbank",
        "website": "https://oriyonbonk.tj/"
    },
    {
        "name": "Тавҳидбонк",
        "id": "tawhidbank",
        "website": "https://www.tawhidbank.tj/"
    },
    {
        "name": "Бонки Эсхата",
        "id": "eskhata",
        "website": "https://eskhata.com/"
    },
    {
        "name": "Коммерсбонк",
        "id": "cbt",
        "website": "https://cbt.tj/"
    },
    {
        "name": "Тиҷорат Бонк",
        "id": "tijoratbank",
        "website": "https://tijoratbank.tj/"
    },
    {
        "name": "Спитамен Бонк",
        "id": "spitamenbank",
        "website": "https://spitamenbank.tj/"
    },
    {
        "name": "Имон Интернешнл Банк",
        "id": "imon",
        "website": "https://imon.tj/"
    },
    {
        "name": "Душанбе Сити",
        "id": "dc",
        "website": "https://dc.tj/"
    },
    {
        "name": "Алиф Бонк",
        "id": "alif",
        "website": "https://alif.tj/"
    },
    {
        "name": "Саноатсодиротбонк",
        "id": "ssb",
        "website": "https://ssb.tj/"
    },
    {
        "name": "IBT",
        "id": "ibt",
        "website": "https://ibt.tj/"
    },
    {
        "name": "ICB",
        "id": "icb",
        "website": "https://icb.tj/"
    },
    {
        "name": "Микрофинансбонк",
        "id": "mfb",
        "website": "https://mfb.tj/"
    },
    {
        "name": "Бонки рушди Тоҷикистон",
        "id": "brt",
        "website": "https://brt.tj/"
    },
    {
        "name": "Ҳумо",
        "id": "humo",
        "website": "https://humo.tj/"
    },
    {
        "name": "Арванд",
        "id": "arvand",
        "website": "https://arvand.tj/"
    },
    {
        "name": "FINCA",
        "id": "finca",
        "website": "https://finca.tj/"
    },
    {
        "name": "Фридом Бонк Тоҷикистон",
        "id": "freedombank",
        "website": "https://freedombank.tj/"
    },
    {
        "name": "Васл Бонк",
        "id": "vaslbank",
        "website": "https://vasl.tj/"
    },
    {
        "name": "Актив Бонк",
        "id": "aktivbank",
        "website": "https://activbank.tj/"
    },
    {
        "name": "Азизи-Молия",
        "id": "azizimoliya",
        "website": "https://azizimoliya.tj/"
    },
    {
        "name": "Матин",
        "id": "matin",
        "website": "https://matin.tj/"
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
    print("CHECKING:", bank["website"])

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
            timeout=60
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
You are a professional AI financial data extraction system.

Your ONLY task is to extract currency exchange rates from website text.

IMPORTANT:

The text may contain:
- menus
- advertisements
- loans
- deposits
- cards
- calculators
- repeated sections
- long website content

IGNORE EVERYTHING except currency exchange rates.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

VERY IMPORTANT RULES:

1. Return ONLY valid JSON.
2. No markdown.
3. No explanations.
4. No comments.
5. No extra text.
6. Never invent values.
7. Search carefully through ALL text.
8. Exchange rates may appear in tables.
9. Buy/sell values may appear in any order.
10. Extract REAL values only.

RULES:

- If currency not found:
buy = "0.0000"
sell = "0.0000"

- If ONLY ONE value exists:
buy = existing value
sell = "0.0000"

- If BOTH values exist:
use real buy/sell values.

OUTPUT FORMAT:

{{
  "USD": {{
    "buy": "0.0000",
    "sell": "0.0000"
  }},
  "EUR": {{
    "buy": "0.0000",
    "sell": "0.0000"
  }},
  "RUB": {{
    "buy": "0.0000",
    "sell": "0.0000"
  }},
  "CNY": {{
    "buy": "0.0000",
    "sell": "0.0000"
  }},
  "KZT": {{
    "buy": "0.0000",
    "sell": "0.0000"
  }}
}}

WEBSITE TEXT:

{markdown[:15000]}
"""

    # ==========================
    # AI REQUEST
    # ==========================

    content = None

    for attempt in range(5):

        print(f"\nAI ATTEMPT: {attempt + 1}")

        try:

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

            print("\n========== AI RESPONSE ==========\n")
            print(json.dumps(ai_data, ensure_ascii=False, indent=2))

            # ==========================
            # CHECK ERRORS
            # ==========================

            if "error" in ai_data:

                print("API ERROR:", ai_data["error"]["message"])

                if ai_data["error"]["code"] == 429:

                    print("RATE LIMIT HIT")
                    break

                time.sleep(10)
                continue

            # ==========================
            # CHECK CHOICES
            # ==========================

            if "choices" not in ai_data:

                print("NO CHOICES FOUND")

                time.sleep(10)
                continue

            content = ai_data["choices"][0]["message"]["content"]

            # ==========================
            # CLEAN JSON
            # ==========================

            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

            # ==========================
            # TEST JSON
            # ==========================

            test_json = json.loads(content)

            print("VALID JSON RECEIVED")

            break

        except Exception as e:

            print("AI ERROR:", e)

            time.sleep(10)

    # ==========================
    # FINAL CHECK
    # ==========================

    if not content:

        print("FAILED TO EXTRACT")
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

    print("BANK ADDED SUCCESSFULLY")

    # ==========================
    # WAIT
    # ==========================

    print("WAITING 3 SECONDS...\n")

    time.sleep(3)

# ==============================
# SAVE JSON
# ==============================

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==============================
# PRINT FINAL JSON
# ==============================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\nDATA SAVED TO data.json")
