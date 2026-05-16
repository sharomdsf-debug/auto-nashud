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
# AI MODELS
# ==============================

models = [
    "openai/gpt-oss-120b:free",
    "deepseek/deepseek-v4-flash:free"
]

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
        "id": "tejaratbank",
        "website": "https://tejaratbank.tj/"
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
# FAILED BANKS
# ==============================

failed_banks = []

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
# LOOP BANKS
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
                "waitFor": 15000
            },
            timeout=60
        )

        data = response.json()

    except Exception as e:

        print("FIRECRAWL ERROR:", e)

        failed_banks.append({
            "bank": bank["name"],
            "website": bank["website"],
            "reason": str(e)
        })

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

        failed_banks.append({
            "bank": bank["name"],
            "website": bank["website"],
            "reason": "NO MARKDOWN"
        })

        continue

    # ==========================
    # AI PROMPT
    # ==========================

    prompt = f"""
You are an advanced AI currency extraction system.

Extract ONLY real exchange rates from the text.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

VERY IMPORTANT RULES:

1. Return ONLY VALID JSON.
2. No markdown.
3. No explanations.
4. No comments.
5. No extra text.
6. Never invent values.
7. Use ONLY values found in text.
8. Ignore phone numbers.
9. Ignore percentages.
10. Ignore credit amounts.
11. Ignore years.
12. Ignore deposit values.
13. Ignore random numbers.
14. ONLY extract currency exchange rates.

If only ONE value exists:
buy = value
sell = value

If both buy and sell exist:
use real values.

If currency not found:
buy = "0.0000"
sell = "0.0000"

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

TEXT:
{markdown[:20000]}
"""

    currencies = None

    # ==========================
    # TRY AI MODELS
    # ==========================

    for model in models:

        print("\n============================")
        print("USING MODEL:", model)

        for attempt in range(3):

            print(f"TRY {attempt + 1}/3")

            try:

                ai_response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0
                    },
                    timeout=120
                )

                ai_data = ai_response.json()

                print("\n========== AI RESPONSE ==========\n")
                print(json.dumps(ai_data, ensure_ascii=False, indent=2))

                # ======================
                # CHECK CHOICES
                # ======================

                if "choices" not in ai_data:

                    print("NO CHOICES FOUND")
                    time.sleep(10)
                    continue

                content = ai_data["choices"][0]["message"]["content"]

                # ======================
                # PARSE JSON
                # ======================

                currencies = json.loads(content)

                print("VALID JSON RECEIVED")

                break

            except Exception as e:

                print("AI ERROR:", e)
                time.sleep(10)

        # ======================
        # IF SUCCESS BREAK
        # ======================

        if currencies is not None:

            print("SUCCESS WITH:", model)
            break

        else:

            print("FAILED MODEL:", model)

    # ==========================
    # FAILED ALL MODELS
    # ==========================

    if currencies is None:

        failed_banks.append({
            "bank": bank["name"],
            "website": bank["website"],
            "reason": "ALL AI MODELS FAILED"
        })

        continue

    # ==========================
    # SAVE BANK
    # ==========================

    final_json["rates"].append({
        "bank_name": bank["name"],
        "bank_id": bank["id"],
        "website": bank["website"],
        "currencies": currencies
    })

    print("BANK ADDED SUCCESSFULLY")

    time.sleep(3)

# ==============================
# SAVE DATA.JSON
# ==============================

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==============================
# SAVE FAILED_BANKS.JSON
# ==============================

with open("failed_banks.json", "w", encoding="utf-8") as f:

    json.dump(failed_banks, f, ensure_ascii=False, indent=2)

# ==============================
# FINAL PRINT
# ==============================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\n========== FAILED BANKS ==========\n")

print(json.dumps(failed_banks, ensure_ascii=False, indent=2))

print("\nDATA SAVED TO data.json")
print("FAILED BANKS SAVED TO failed_banks.json")
