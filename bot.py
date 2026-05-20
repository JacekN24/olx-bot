import requests
from bs4 import BeautifulSoup
import re
import json
import os

keywords = ["amiga", "commodore", "atari", "zx spectrum", "technics", "subwoofer"]

blocked = [
    "koparka", "kosiarka", "mulczer",
    "ramie", "ramię", "budowlana",
    "ps3", "playstation", "simulator", "kierownica"
]

TOKEN = "8758184901:AAHAbh8W8tAFFUg9q8RnzJ1s7mQ53UH_QiE"
CHAT_ID = "7950132781"

SEEN_FILE = "seen.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def is_ok(title):
    t = title.lower()
    return not any(word in t for word in blocked)


def get_price(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None


def is_deal(title, price):
    t = title.lower()

    deal_words = ["okazja", "tanio", "pilne", "sprzedam szybko", "nie znam"]

    if any(k in t for k in deal_words):
        return True

    if price:
        if "amiga" in t and price < 300:
            return True
        if "technics" in t and price < 250:
            return True
        if "atari" in t and price < 200:
            return True
        if price < 150:
            return True

    return False


def run():
    seen = load_seen()

    for word in keywords:
        url = f"https://www.olx.pl/d/oferty/q-{word}/?search%5Border%5D=created_at:desc"

        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        ads = soup.select("a")

        count = 0

        for ad in ads:
            link = ad.get("href")

            if link and "/d/oferta/" in link:
                link = "https://www.olx.pl" + link.split("?")[0]

                if link in seen:
                    continue

                title = ad.text.strip()

                if not is_ok(title):
                    continue

                price = get_price(title)

                msg = f"🆕 {title}\n"

                if price:
                    msg += f"💰 {price} PLN\n"

                if is_deal(title, price):
                    msg += "🔥 OKAZJA !!!\n"

                msg += link

                send(msg)

                seen.add(link)

                count += 1

                if count >= 3:
                    break

    save_seen(seen)


if __name__ == "__main__":
    run()
