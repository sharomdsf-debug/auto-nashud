import requests
import os
import json

FIRECRAWL_API = os.getenv("FIRECRAWL_API")

OPENROUTER_API = "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"

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

    prompt = f"""
Аз ҳамин матн танҳо қурби асъорро ёб.

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
{website_text[:5000]}
"""

    # OPENROUTER AI
    ai_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct:free",
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
        timeout=120
    )

    result = ai_response.json()

    print("\n===== OPENROUTER RESPONSE =====\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n===== AI JSON =====\n")

    try:
        print(
            result["choices"][0]["message"]["content"]
        )

    except Exception as e:
        print("AI ERROR")
        print(e)
