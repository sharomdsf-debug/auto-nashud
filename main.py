import requests
import os
import json

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
GROQ_API = os.getenv("GROQ_API")

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

    # GROQ AI
    ai_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
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

    print("\n===== GROQ RESPONSE =====\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n===== AI JSON =====\n")

    if "choices" in result:
        print(
            result["choices"][0]["message"]["content"]
        )
    else:
        print("GROQ ERROR")
