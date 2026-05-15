import requests
import os
import json

# FIRECRAWL API
FIRECRAWL_API = os.getenv("FIRECRAWL_API")

# GEMINI API
GEMINI_API = "AIzaSyA5M1mjVa9Yx5s5XoRGdZioCRr3su_A8Rk"

banks = [
    "https://www.tawhidbank.tj/"
]

for url in banks:

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
        }
    )

    data = response.json()

    if "data" not in data or "markdown" not in data["data"]:

        print("ERROR:")
        print(data)
        continue

    website_text = data["data"]["markdown"]

    print("\n========== WEBSITE TEXT LOADED ==========\n")

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
Аз ҳамин матн танҳо қурби асъорро ёб.

Асъорҳо:
USD
EUR
RUB

Фақат JSON баргардон.

Формат:

{{
  "usd_buy": "",
  "usd_sell": "",
  "eur_buy": "",
  "eur_sell": "",
  "rub_buy": "",
  "rub_sell": ""
}}

TEXT:
{website_text[:12000]}
"""

    # =========================
    # GEMINI REQUEST
    # =========================

    gemini_response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        timeout=120
    )

    print("\n========== GEMINI RAW RESPONSE ==========\n")

    print(gemini_response.text)

    # =========================
    # PARSE RESPONSE
    # =========================

    try:

        result = gemini_response.json()

        print("\n========== FINAL JSON ==========\n")

        print(
            result["candidates"][0]["content"]["parts"][0]["text"]
        )

    except Exception as e:

        print("\nGEMINI ERROR")
        print(str(e))
