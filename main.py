import requests
import json

# API KEYS
FIRECRAWL_API = "FIRECRAWL_API_HERE"

DEEPSEEK_API = "sk-825822e3551848e58b03d5bb284ea8cf"

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
print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

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
Аз ҳамин матн қурби асъорро ёб.

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
# DEEPSEEK AI
# =========================

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

print("\n===== DEEPSEEK RAW RESPONSE =====\n")
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
        print("DEEPSEEK ERROR")

except Exception as e:
    print("\nJSON ERROR")
    print(str(e))
