import requests
import os
import json
import time
import copy
import re
from datetime import datetime

# =========================================================
# API
# =========================================================

FIRECRAWL_API = os.getenv("FIRECRAWL_API")
OPENROUTER_API = os.getenv("OPENROUTER_API")

# =========================================================
# AI MODELS
# =========================================================

MODELS = [
    "openai/gpt-oss-120b:free",
    "deepseek/deepseek-v3-base:free",
    "qwen/qwen3-coder:free"
]

# =========================================================
# BANKS
# =========================================================

ALL_BANKS = [
    {"name": "Бонки Миллии Тоҷикистон", "id": "nbt", "website": "https://nbt.tj/"},
    {"name": "Амонатбонк", "id": "amonatbonk", "website": "https://amonatbonk.tj/"},
    {"name": "Ориёнбонк", "id": "oriyonbank", "website": "https://oriyonbonk.tj/"},
    {"name": "Тавҳидбонк", "id": "tawhidbank", "website": "https://www.tawhidbank.tj/"},
    {"name": "Бонки Эсхата", "id": "eskhata", "website": "https://eskhata.com/"},
    {"name": "Коммерсбонк", "id": "cbt", "website": "https://cbt.tj/"},
    {"name": "Тиҷорат Бонк", "id": "tejaratbank", "website": "https://tejaratbank.tj/"},
    {"name": "Спитамен Бонк", "id": "spitamenbank", "website": "https://spitamenbank.tj/"},
    {"name": "Имон Интернешнл Банк", "id": "imon", "website": "https://imon.tj/"},
    {"name": "Душанбе Сити", "id": "dc", "website": "https://dc.tj/"},
    {"name": "Алиф Бонк", "id": "alif", "website": "https://alif.tj/"},
    {"name": "Саноатсодиротбонк", "id": "ssb", "website": "https://ssb.tj/"},
    {"name": "IBT", "id": "ibt", "website": "https://ibt.tj/"},
    {"name": "ICB", "id": "icb", "website": "https://icb.tj/"},
    {"name": "Микрофинансбонк", "id": "mfb", "website": "https://mfb.tj/"},
    {"name": "Бонки рушди Тоҷикистон", "id": "brt", "website": "https://brt.tj/"},
    {"name": "Ҳумо", "id": "humo", "website": "https://humo.tj/"},
    {"name": "Арванд", "id": "arvand", "website": "https://arvand.tj/"},
    {"name": "FINCA", "id": "finca", "website": "https://finca.tj/"},
    {"name": "Фридом Бонк Тоҷикистон", "id": "freedombank", "website": "https://freedombank.tj/"},
    {"name": "Васл Бонк", "id": "vaslbank", "website": "https://vasl.tj/"},
    {"name": "Актив Бонк", "id": "aktivbank", "website": "https://activbank.tj/"},
    {"name": "Азизи-Молия", "id": "azizimoliya", "website": "https://azizimoliya.tj/"},
    {"name": "Матин", "id": "matin", "website": "https://matin.tj/"}
]

# =========================================================
# SPLIT INTO 8 PARTS
# =========================================================

PARTS = [ALL_BANKS[i:i+3] for i in range(0, len(ALL_BANKS), 3)]

# =========================================================
# VALIDATION
# =========================================================

VALID_RANGES = {
    "USD": (8.0, 12.0),
    "EUR": (8.0, 14.0),
    "RUB": (0.08, 0.25),
    "CNY": (1.0, 2.5),
    "KZT": (0.010, 0.060)
}

CURRENCIES = list(VALID_RANGES.keys())

EMPTY = {
    c: {"buy": "0.0000", "sell": "0.0000"}
    for c in CURRENCIES
}

# =========================================================
# HELPERS
# =========================================================

def validate(currency, value):
    try:
        num = float(str(value).replace(",", "."))
        lo, hi = VALID_RANGES[currency]

        if lo <= num <= hi:
            return f"{num:.4f}"

        return "0.0000"

    except:
        return "0.0000"


def clean_json(data):
    result = copy.deepcopy(EMPTY)

    for cur in CURRENCIES:

        if cur not in data:
            continue

        result[cur]["buy"] = validate(
            cur,
            data[cur].get("buy", "0")
        )

        result[cur]["sell"] = validate(
            cur,
            data[cur].get("sell", "0")
        )

    return result


def merge(base, extra):

    result = copy.deepcopy(base)

    for cur in CURRENCIES:

        if (
            result[cur]["buy"] == "0.0000"
            and extra[cur]["buy"] != "0.0000"
        ):
            result[cur]["buy"] = extra[cur]["buy"]

        if (
            result[cur]["sell"] == "0.0000"
            and extra[cur]["sell"] != "0.0000"
        ):
            result[cur]["sell"] = extra[cur]["sell"]

    return result


def count_found(data):

    total = 0

    for cur in CURRENCIES:

        if (
            data[cur]["buy"] != "0.0000"
            or data[cur]["sell"] != "0.0000"
        ):
            total += 1

    return total


# =========================================================
# FIRECRAWL
# =========================================================

def scrape(url):

    print(f"\nSCRAPING: {url}")

    try:

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": False,
                "waitFor": 15000
            },
            timeout=180
        )

        data = response.json()

        markdown = data.get("data", {}).get("markdown", "")

        print(f"MARKDOWN: {len(markdown)} chars")

        return markdown

    except Exception as e:

        print("SCRAPE ERROR:", e)

        return ""


# =========================================================
# AI STAGE 1
# FIND CURRENCY SECTION
# =========================================================

SECTION_PROMPT = """
You are extracting ONLY the currency exchange section from a bank website.

IMPORTANT:
- Return ONLY raw text.
- DO NOT summarize.
- DO NOT explain.
- DO NOT output JSON.
- Find ONLY the part containing exchange rates.
- Ignore menus, footer, contacts, news, loans, cards.

The section MUST contain:
USD, EUR, RUB, CNY or KZT.

Return maximum 2500 characters.

TEXT:
"""


def find_currency_section(markdown):

    markdown = markdown[:40000]

    for model in MODELS:

        print(f"\nSECTION MODEL: {model}")

        for attempt in range(2):

            try:

                response = requests.post(
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
                                "content": SECTION_PROMPT + markdown
                            }
                        ],
                        "temperature": 0,
                        "max_tokens": 1200
                    },
                    timeout=180
                )

                data = response.json()

                if "choices" not in data:
                    continue

                text = data["choices"][0]["message"]["content"]

                if len(text) > 100:
                    print("SECTION FOUND")
                    return text

            except Exception as e:

                print("SECTION ERROR:", e)

            time.sleep(5)

    return markdown[:2500]


# =========================================================
# AI STAGE 2
# EXTRACT JSON
# =========================================================

JSON_PROMPT = """
Extract REAL bank exchange rates against TJS.

STRICT RULES:
- Return ONLY JSON.
- Never explain.
- Never add markdown.
- Use ONLY numbers from the text.
- Never invent values.
- Ignore phone numbers, years, loan rates, percentages.

IMPORTANT:
- Some banks may have only BUY and no SELL.
- If sell missing -> "0.0000"
- If currency missing -> "0.0000"

VALID RANGES:
USD: 8-12
EUR: 8-14
RUB: 0.08-0.25
CNY: 1-2.5
KZT: 0.01-0.06

OUTPUT FORMAT:

{
  "USD": {"buy":"0.0000","sell":"0.0000"},
  "EUR": {"buy":"0.0000","sell":"0.0000"},
  "RUB": {"buy":"0.0000","sell":"0.0000"},
  "CNY": {"buy":"0.0000","sell":"0.0000"},
  "KZT": {"buy":"0.0000","sell":"0.0000"}
}

TEXT:
"""


def extract_rates(text):

    best = copy.deepcopy(EMPTY)

    for model in MODELS:

        print(f"\nEXTRACT MODEL: {model}")

        for attempt in range(3):

            try:

                response = requests.post(
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
                                "content": JSON_PROMPT + text
                            }
                        ],
                        "temperature": 0,
                        "max_tokens": 300
                    },
                    timeout=180
                )

                data = response.json()

                if "choices" not in data:
                    continue

                raw = data["choices"][0]["message"]["content"]

                raw = raw.replace("```json", "")
                raw = raw.replace("```", "")

                start = raw.find("{")
                end = raw.rfind("}") + 1

                if start == -1:
                    continue

                parsed = json.loads(raw[start:end])

                cleaned = clean_json(parsed)

                found = count_found(cleaned)

                print(f"FOUND: {found}/5")

                if found > count_found(best):
                    best = cleaned

                if found >= 3:
                    return cleaned

            except Exception as e:

                print("EXTRACT ERROR:", e)

            time.sleep(5)

    return best


# =========================================================
# PROCESS BANK
# =========================================================

def process_bank(bank):

    print("\n" + "="*60)
    print(bank["name"])
    print("="*60)

    markdown = scrape(bank["website"])

    if not markdown:

        return {
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "website": bank["website"],
            "currencies": copy.deepcopy(EMPTY)
        }

    # ==========================
    # STAGE 1
    # ==========================

    section = find_currency_section(markdown)

    print(f"SECTION SIZE: {len(section)}")

    # ==========================
    # STAGE 2
    # ==========================

    currencies = extract_rates(section)

    print(f"FINAL FOUND: {count_found(currencies)}/5")

    return {
        "bank_name": bank["name"],
        "bank_id": bank["id"],
        "website": bank["website"],
        "currencies": currencies
    }


# =========================================================
# PROCESS PART
# =========================================================

def process_part(part, filename):

    result = {
        "rates": []
    }

    for bank in part:

        item = process_bank(bank)

        result["rates"].append(item)

        time.sleep(5)

    with open(filename, "w", encoding="utf-8") as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nSAVED: {filename}")


# =========================================================
# RUN
# =========================================================

for index, part in enumerate(PARTS):

    print("\n" + "#"*70)
    print(f"PART {index+1}/{len(PARTS)}")
    print("#"*70)

    process_part(
        part,
        f"part{index+1}.json"
    )

    if index < len(PARTS)-1:
        time.sleep(20)


# =========================================================
# MERGE
# =========================================================

all_rates = []

for i in range(1, len(PARTS)+1):

    with open(f"part{i}.json", encoding="utf-8") as f:

        data = json.load(f)

        all_rates.extend(data["rates"])


final = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": all_rates
}

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(
        final,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\nDONE")
print(json.dumps(final, ensure_ascii=False, indent=2))
