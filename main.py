import requests
import os

API_KEY = os.getenv("FIRECRAWL_API")

banks = [
    "https://google.com",
    "https://example.com"
]

for url in banks:

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

    print(data)
