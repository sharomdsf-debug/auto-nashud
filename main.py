import requests
import os

API_KEY = os.getenv("FIRECRAWL_API")

banks = [
    "https://dc.tj/",
    "https://www.tawhidbank.tj/personal",
    "https://eskhata.com/"
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
            "formats": ["markdown"]
        }
    )

    data = response.json()

    if "data" in data:
        print(data["data"]["markdown"][:5000])
    else:
        print(data)
