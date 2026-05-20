import requests
from bs4 import BeautifulSoup

keywords = ["amiga", "commodore", "atari", "zx spectrum", "technics", "subwoofer"]

blocked = ["koparka", "kosiarka", "mulczer", "ramie", "ramię", "budowlana"]

TOKEN = "8758184901:AAHAbh8W8tAFFUg9q8RnzJ1s7mQ53UH_QiE"
CHAT_ID = "7950132781"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def is_ok(title):
    t = title.lower()
    if any(word in t for word in blocked):
        return False
    return True

def run():
    for word in keywords:
        url = f"https://www.olx.pl/d/oferty/q-{word}/?search%5Border%5D=created_at:desc"

        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        ads = soup.select("a")

        for ad in ads:
            link = ad.get("href")

            if link and "/d/oferta/" in link:
                link = "https://www.olx.pl" + link.split("?")[0]
                title = ad.text.strip()

                if is_ok(title):
                    msg = f"🔥 OLX ALERT:\n{title}\n{link}"
                    send_telegram(msg)

if __name__ == "__main__":
    run()
``
