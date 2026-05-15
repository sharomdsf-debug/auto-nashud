import requests
import os
import json

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
DEEPSEEK_API = os.getenv("DEEPSEEK_API")

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
        print("FIRECRAWL ERROR:")
        print(data)
        continue

    website_text = data["data"]["markdown"]

    print("TEXT LOADED")

    # DEEPSEEK
    ai_response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": """
Ту AI барои истихроҷи қурби асъор ҳастӣ.

Фақат JSON баргардон.

Фақат USD EUR RUB гир.

Формат:

{
  "usd_buy": "",
  "usd_sell": "",
  "eur_buy": "",
  "eur_sell": "",
  "rub_buy": "",
  "rub_sell": ""
}
"""
                },
                {
                    "role": "user",
                    "content": website_text
                }
            ],
            "temperature": 0
        }
    )

    result = ai_response.json()

    print("\n===== DEEPSEEK RESPONSE =====\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n===== AI JSON =====\n")

    if "choices" in result:
        print(
            result["choices"][0]["message"]["content"]
        )
    else:
        print("DEEPSEEK ERROR")
