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
# BANKS (EASY WEBSITES)
# ==========================================

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
        "name": "Тавҳидбонк",
        "id": "tawhid",
        "website": "https://www.tawhidbank.tj"
    },
    {
        "name": "Душанбе Сити",
        "id": "dushanbe_city",
        "website": "https://dc.tj"
    },
    {
        "name": "IBT",
        "id": "ibt",
        "website": "https://ibt.tj"
    }
]

# ==========================================
# EMPTY CURRENCIES
# ==========================================

EMPTY_CURRENCIES = {
    "USD": {"buy": "0.0000", "sell": "0.0000"},
    "EUR": {"buy": "0.0000", "sell": "0.0000"},
    "RUB": {"buy": "0.0000", "sell": "0.0000"},
    "CNY": {"buy": "0.0000", "sell": "0.0000"},
    "KZT": {"buy": "0.0000", "sell": "0.0000"}
}

# ==========================================
# FINAL JSON
# ==========================================

final_json = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": []
}

# ==========================================
# LOOP
# ==========================================

for bank in banks:

    print("\n==============================")
    print("Checking:", bank["website"])

    markdown = ""

    # ======================================
    # FIRECRAWL
    # ======================================

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
                "onlyMainContent": False,
                "waitFor": 10000
            },
            timeout=60
        )

        data = response.json()

        print("\n========== FIRECRAWL ==========\n")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])

    except Exception as e:

        print("FIRECRAWL ERROR:", e)

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": EMPTY_CURRENCIES
        })

        continue

    # ======================================
    # GET MARKDOWN
    # ======================================

    if data.get("success") and data.get("data", {}).get("markdown"):

        markdown = data["data"]["markdown"]

        print("\nTEXT LOADED")

    else:

        print("\nNO DATA")

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": EMPTY_CURRENCIES
        })

        continue

    # ======================================
    # AI PROMPT
    # ======================================

    prompt = f"""
You are an AI currency extraction system.

Extract ONLY exchange rates from website text.

SUPPORTED CURRENCIES:
USD
EUR
RUB
CNY
KZT

IMPORTANT RULES:

1. Return ONLY VALID JSON
2. No markdown
3. No explanation
4. No comments
5. Never invent values

6. If currency not found:
buy = "0.0000"
sell = "0.0000"

7. If ONLY ONE rate exists:
buy = rate
sell = "0.0000"

8. If BOTH buy and sell exist:
use real values

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

    # ======================================
    # AI REQUEST
    # ======================================

    try:

        ai_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",
                "X-Title": "ASOR TJ"
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
        print(json.dumps(ai_data, ensure_ascii=False, indent=2)[:4000])

        content = ai_data["choices"][0]["message"]["content"]

    except Exception as e:

        print("AI ERROR:", e)

        final_json["rates"].append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "currencies": EMPTY_CURRENCIES
        })

        continue

    # ======================================
    # JSON PARSE
    # ======================================

    try:

        currencies = json.loads(content)

    except Exception as e:

        print("JSON ERROR:", e)

        currencies = EMPTY_CURRENCIES

    # ======================================
    # ADD TO FINAL JSON
    # ======================================

    final_json["rates"].append({
        "bank_name": bank["name"],
        "bank_id": bank["id"],
        "currencies": currencies
    })

# ==========================================
# SAVE JSON
# ==========================================

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(final_json, f, ensure_ascii=False, indent=2)

# ==========================================
# PRINT FINAL JSON
# ==========================================

print("\n========== FINAL JSON ==========\n")

print(json.dumps(final_json, ensure_ascii=False, indent=2))

print("\nDATA SAVED TO data.json")
