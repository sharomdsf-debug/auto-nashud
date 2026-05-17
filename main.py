import requests
import os
import json
import time
import re
import copy
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

PARTS = [
    ALL_BANKS[0:3],
    ALL_BANKS[3:6],
    ALL_BANKS[6:9],
    ALL_BANKS[9:12],
    ALL_BANKS[12:15],
    ALL_BANKS[15:18],
    ALL_BANKS[18:21],
    ALL_BANKS[21:24]
]

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
    c: {
        "buy": "0.0000",
        "sell": "0.0000"
    }
    for c in CURRENCIES
}

# =========================================================
# KEYWORDS
# =========================================================

KEYWORDS = [
    "usd", "eur", "rub", "cny", "kzt",
    "курс", "қурб", "валют", "асъор",
    "exchange", "currency",
    "харид", "фурӯш",
    "buy", "sell",
    "покупка", "продажа"
]

# =========================================================
# HELPERS
# =========================================================

def validate_value(currency, value):
    try:
        value = str(value).replace(",", ".").strip()
        num = float(value)

        low, high = VALID_RANGES[currency]

        if low <= num <= high:
            return f"{num:.4f}"

        return "0.0000"

    except:
        return "0.0000"


def clean_ai_json(data):
    result = copy.deepcopy(EMPTY)

    for currency in CURRENCIES:

        if currency not in data:
            continue

        result[currency]["buy"] = validate_value(
            currency,
            data[currency].get("buy", "0")
        )

        result[currency]["sell"] = validate_value(
            currency,
            data[currency].get("sell", "0")
        )

    return result


def merge_currencies(base, extra):

    result = copy.deepcopy(base)

    for currency in CURRENCIES:

        if (
            result[currency]["buy"] == "0.0000"
            and extra[currency]["buy"] != "0.0000"
        ):
            result[currency]["buy"] = extra[currency]["buy"]

        if (
            result[currency]["sell"] == "0.0000"
            and extra[currency]["sell"] != "0.0000"
        ):
            result[currency]["sell"] = extra[currency]["sell"]

    return result


def count_found(currencies):

    total = 0

    for currency in CURRENCIES:

        if (
            currencies[currency]["buy"] != "0.0000"
            or currencies[currency]["sell"] != "0.0000"
        ):
            total += 1

    return total


# =========================================================
# SMART CHUNKS
# =========================================================

CHUNK_SIZE = 40000
OVERLAP = 4000
MAX_CHUNKS = 5

def build_chunks(markdown):

    text = markdown.replace("\r", "\n")

    chunks = []

    step = CHUNK_SIZE - OVERLAP

    for i in range(0, len(text), step):

        chunk = text[i:i + CHUNK_SIZE]

        lower = chunk.lower()

        score = 0

        for keyword in KEYWORDS:
            score += lower.count(keyword)

        chunks.append({
            "score": score,
            "text": chunk
        })

    chunks.sort(key=lambda x: x["score"], reverse=True)

    final_chunks = []

    for item in chunks[:MAX_CHUNKS]:
        final_chunks.append(item["text"])

    if not final_chunks:
        final_chunks.append(text[:CHUNK_SIZE])

    return final_chunks


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

        print(f"MARKDOWN SIZE: {len(markdown)}")

        return markdown

    except Exception as e:

        print("SCRAPE ERROR:", e)

        return ""


# =========================================================
# AI PROMPT
# =========================================================

PROMPT = """
Extract REAL bank currency exchange rates against TJS.

VERY IMPORTANT:

ALL BANKS HAVE REAL EXCHANGE RATES.
You must carefully search the website text and find them.

Currencies:
USD
EUR
RUB
CNY
KZT

Rules:

- Return ONLY valid JSON.
- No markdown.
- No explanations.
- Use ONLY numbers found in the text.
- Never invent values.
- Ignore:
  phone numbers,
  years,
  loan percentages,
  deposit percentages,
  card limits,
  menu numbers.

VALID RANGES:

USD: 8.0 - 12.0
EUR: 8.0 - 14.0
RUB: 0.08 - 0.25
CNY: 1.0 - 2.5
KZT: 0.010 - 0.060

VERY IMPORTANT:

- If currency truly not found:
  buy = "0.0000"
  sell = "0.0000"

- If only one value exists:
  put it into buy
  sell = "0.0000"

- NEVER copy values from another currency.

STRICT JSON FORMAT:

{
  "USD": {"buy":"0.0000","sell":"0.0000"},
  "EUR": {"buy":"0.0000","sell":"0.0000"},
  "RUB": {"buy":"0.0000","sell":"0.0000"},
  "CNY": {"buy":"0.0000","sell":"0.0000"},
  "KZT": {"buy":"0.0000","sell":"0.0000"}
}

WEBSITE TEXT:
"""


# =========================================================
# AI CALL
# =========================================================

def ask_ai(chunk):

    for model in MODELS:

        print(f"\nMODEL: {model}")

        for attempt in range(3):

            print(f"TRY {attempt + 1}/3")

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
                                "content": PROMPT + chunk
                            }
                        ],
                        "temperature": 0,
                        "max_tokens": 300
                    },
                    timeout=180
                )

                data = response.json()

                if "choices" not in data:
                    print("NO CHOICES")
                    time.sleep(10)
                    continue

                content = data["choices"][0]["message"]["content"]

                content = re.sub(r"```json", "", content)
                content = re.sub(r"```", "", content).strip()

                start = content.find("{")
                end = content.rfind("}") + 1

                if start == -1:
                    raise Exception("JSON NOT FOUND")

                content = content[start:end]

                parsed = json.loads(content)

                cleaned = clean_ai_json(parsed)

                found = count_found(cleaned)

                print(f"FOUND: {found}/5")

                if found > 0:
                    return cleaned

            except Exception as e:

                print("AI ERROR:", e)

            time.sleep(8)

    return copy.deepcopy(EMPTY)


# =========================================================
# PROCESS BANK
# =========================================================

def process_bank(bank):

    print("\n" + "=" * 60)
    print(bank["name"])
    print(bank["website"])
    print("=" * 60)

    markdown = scrape(bank["website"])

    currencies = copy.deepcopy(EMPTY)

    if not markdown:

        print("NO MARKDOWN")

        return {
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "website": bank["website"],
            "currencies": currencies
        }

    chunks = build_chunks(markdown)

    print(f"CHUNKS: {len(chunks)}")

    for index, chunk in enumerate(chunks):

        print(f"\nCHUNK {index + 1}")

        ai_result = ask_ai(chunk)

        currencies = merge_currencies(
            currencies,
            ai_result
        )

        print(f"TOTAL FOUND: {count_found(currencies)}/5")

        time.sleep(3)

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

        bank_data = process_bank(bank)

        result["rates"].append(bank_data)

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

    print("\n" + "#" * 70)
    print(f"PART {index + 1}/{len(PARTS)}")
    print("#" * 70)

    process_part(
        part,
        f"part{index + 1}.json"
    )

    if index < len(PARTS) - 1:

        print("\nWAITING 20 SECONDS...\n")

        time.sleep(20)


# =========================================================
# MERGE JSON
# =========================================================

all_rates = []

for i in range(1, len(PARTS) + 1):

    with open(f"part{i}.json", encoding="utf-8") as f:

        data = json.load(f)

        all_rates.extend(data["rates"])


final_json = {
    "project_name": "ASOR TJ",
    "last_updated": "🔹" + datetime.now().strftime("%d.%m.%Y %H:%M"),
    "base_currency": "TJS",
    "status": "success",
    "rates": all_rates
}

with open("data.json", "w", encoding="utf-8") as f:

    json.dump(
        final_json,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\nDONE")
print(json.dumps(final_json, ensure_ascii=False, indent=2))
