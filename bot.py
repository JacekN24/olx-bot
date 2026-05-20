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


