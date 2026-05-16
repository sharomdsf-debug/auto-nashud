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
        "website": "https://aktivbank.tj/"
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
You are an AI currency extraction system.

Extract ONLY exchange rates from the text.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. No markdown.
3. No explanation.
4. No comments.
5. If currency not found:
buy = "0.0000"
sell = "0.0000"

6. If ONLY ONE rate exists:
buy = existing rate
sell = "0.0000"

7. If BOTH buy and sell exist:
use real values.

8. Never invent values.

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
{markdown[:12000]}
"""

    # ==========================
    # AI REQUEST WITH INFINITE RETRY
    # ==========================

    content = None

    while True:

        print("\nTRYING AI REQUEST...")

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
            # CHECK RESPONSE
            # ==========================

            if "choices" not in ai_data:

                print("NO CHOICES FOUND")
                print("WAITING 10 SECONDS...")
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

            print("RETRY AFTER 10 SECONDS")

            time.sleep(10)

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
    # WAIT BETWEEN BANKS
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
