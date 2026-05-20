import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

# 🔎 czego szukasz
keywords = ["amiga", "commodore", "atari", "zx spectrum", "technics", "subwoofer"]

# ❌ śmieci
blocked = [
    "koparka", "kosiarka", "mulczer", "ramie", "ramię",
    "budowlana", "ps3", "playstation", "simulator", "kierownica"
]

TOKEN = "8758184901:AAHAbh8W8tAFFUg9q8RnzJ1s7mQ53UH_QiE"
CHAT_ID = "7950132781"

SEEN_FILE = "seen.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ✅ TELEGRAM
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ✅ wczytaj widziane
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


# ✅ zapisz widziane
def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


# ✅ filtr śmieci
def is_ok(title):
    t = title.lower()
    return not any(word in t for word in blocked)


# ✅ WYCIĄGNIJ CENĘ
def get_price(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None


# ✅ czy okazja
def is_deal(title, price):
    t = title.lower()

    # słowa okazji
    keywords = ["okazja", "tanio", "pilne", "sprzedam szybko", "nie znam"]

    if any(k in t for k in keywords):
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


# 🔥 GŁÓWNA FUNKCJA
def run():
    seen = load_seen()

    for word in keywords:
