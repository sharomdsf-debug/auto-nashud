import requests
import os

API_KEY = os.getenv("FIRECRAWL_API")

banks = [
    "https://www.tawhidbank.tj/"
]

for url in banks:

    print("\n====================")
    print("Checking:", url)

    response = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "url": url,
            "formats": ["markdown"],
            "waitFor": 10000
        }
    )

    data = response.json()

    if "data" in data and "markdown" in data["data"]:

        print("\n========== WEBSITE TEXT ==========\n")

        print(data["data"]["markdown"])

        print("\n========== END ==========\n")

    else:
        print("ERROR:")
        print(data)
