import requests
import json

# API KEYS
FIRECRAWL_API = "fc-14ada6fed79d4c0f9c39ad1bf213aad3"

OPENROUTER_API = "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"

# WEBSITE
url = "https://www.tawhidbank.tj/"

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
    },
    timeout=120
)

data = response.json()

print("\n===== FIRECRAWL RESPONSE =====\n")
print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])

# CHECK
if "data" not in data:
    print("\nFIRECRAWL ERROR")
    exit()

website_text = data["data"]["markdown"]

print("\nTEXT LOADED")

# =========================
# PROMPT
# =========================

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
{website_text[:6000]}
"""

# =========================
# OPENROUTER AI
# =========================

ai_response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "currency-parser"
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

print("\n===== OPENROUTER RAW RESPONSE =====\n")
print(ai_response.text)

# =========================
# JSON PARSE
# =========================

try:

    result = ai_response.json()

    print("\n===== AI RESPONSE =====\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n===== FINAL JSON =====\n")

    if "choices" in result:
        print(
            result["choices"][0]["message"]["content"]
        )
    else:
        print("OPENROUTER ERROR")

except Exception as e:
    print("\nJSON ERROR")
    print(str(e))
