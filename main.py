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
# ALL BANKS
# ==============================

all_banks = [
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
# SPLIT BANKS
# ==============================

part1_banks = all_banks[:12]
part2_banks = all_banks[12:]

# ==============================
# EMPTY CURRENCIES
# ==============================

EMPTY_CURRENCIES = {
    "USD": {"buy": "0.0000", "sell": "0.0000"},
    "EUR": {"buy": "0.0000", "sell": "0.0000"},
    "RUB": {"buy": "0.0000", "sell": "0.0000"},
    "CNY": {"buy": "0.0000", "sell": "0.0000"},
    "KZT": {"buy": "0.0000", "sell": "0.0000"}
}

# ==============================
# PROCESS FUNCTION
# ==============================

def process_banks(bank_list, filename):

    result = {
        "rates": []
    }

    for bank in bank_list:

        print("\n============================")
        print("CHECKING:", bank["website"])

        currencies = None

        # ==========================
        # FIRECRAWL
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

            currencies = EMPTY_CURRENCIES.copy()

        # ==========================
        # GET MARKDOWN
        # ==========================

        markdown = ""

        if currencies is None:

            if "data" in data and "markdown" in data["data"]:

                markdown = data["data"]["markdown"]

                print("TEXT LOADED")

            else:

                print("NO MARKDOWN")

                currencies = EMPTY_CURRENCIES.copy()

        # ==========================
        # AI EXTRACTION
        # ==========================

        if currencies is None:

            prompt = f"""
You are a professional AI currency extraction system.

Extract ONLY real exchange rates.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. No markdown.
3. No explanations.
4. Never invent values.
5. Ignore phone numbers.
6. Ignore years.
7. Ignore percentages.
8. Ignore credit amounts.
9. Ignore deposit amounts.
10. Ignore random numbers.

VERY IMPORTANT:

If currency does NOT exist:
buy = "0.0000"
sell = "0.0000"

If ONLY one rate exists:
buy = real value
sell = "0.0000"

If BOTH exist:
use real values.

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
{markdown[-25000:]}
"""

            # ==========================
            # TRY MODELS
            # ==========================

            for model in models:

                print("\nUSING MODEL:", model)

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

                        print(json.dumps(ai_data, ensure_ascii=False, indent=2))

                        if "choices" not in ai_data:

                            print("NO CHOICES")

                            time.sleep(10)

                            continue

                        content = ai_data["choices"][0]["message"]["content"]

                        content = content.replace("```json", "")
                        content = content.replace("```", "")
                        content = content.strip()

                        currencies = json.loads(content)

                        print("SUCCESS")

                        break

                    except Exception as e:

                        print("AI ERROR:", e)

                        time.sleep(10)

                if currencies is not None:

                    break

        # ==========================
        # FALLBACK
        # ==========================

        if currencies is None:

            currencies = EMPTY_CURRENCIES.copy()

        # ==========================
        # SAVE BANK
        # ==========================

        result["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "website": bank["website"],
            "currencies": currencies
        })

        print("BANK ADDED")

        time.sleep(3)

    # ==========================
    # SAVE PART JSON
    # ==========================

    with open(filename, "w", encoding="utf-8") as f:

        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSAVED: {filename}")

# ==============================
# RUN PART 1
# ==============================

print("\n============================")
print("STARTING PART 1")
print("============================")

process_banks(part1_banks, "part1.json")

# ==============================
# WAIT
# ==============================

print("\nWAITING 20 SECONDS...\n")

time.sleep(20)

# ==============================
# RUN PART 2
# ==============================

print("\n============================")
print("STARTING PART 2")
print("============================")

process_banks(part2_banks, "part2.json")

# ==============================
# MERGE JSON
# ==============================

with open("part1.json", "r", encoding="utf-8") as f:
    part1 = json.load(f)

with open("part2.json", "r", encoding="utf-8") as f:
    part2 = json.load(f)

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": part1["rates"] + part2["rates"]
}

# ==============================
# SAVE FINAL JSON
# ==============================

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==============================
# PRINT FINAL
# ==============================

print("\n============================")
print("FINAL JSON CREATED")
print("============================")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\nSAVED TO data.json")
