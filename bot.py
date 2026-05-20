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


# -------- TELEGRAM --------
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# -------- PAMIĘĆ --------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


# -------- FILTRY --------
def is_ok(title):
    t = title.lower()
    return not any(word in t for word in blocked)


def get_price_from_page(link):
    try:
        r = requests.get(link, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text(" ", strip=True).lower()

        match = re.search(r'(\d{2,6})\s?zł', text)
        if match:
            return int(match.group(1))
    except:
        return None

    return None


def score_deal(title, price):
    t = title.lower()
    score = 0

    # 🔥 słowa kluczowe
    if "okazja" in t: score += 3
    if "tanio" in t: score += 2
    if "pilne" in t: score += 2
    if "sprzedam szybko" in t: score += 3
    if "nie znam" in t: score += 4

    # 💰 ceny
    if price:
        if "amiga" in t:
            if price < 300: score += 5
            if price < 200: score += 8

        if "technics" in t:
            if price < 250: score += 5

        if "atari" in t:
            if price < 200: score += 5

        if price < 150:
            score += 4

        if price < 100:
            score += 6

    return score


def classify(score):
    if score >= 8:
        return "🔥 MEGA OKAZJA"
    elif score >= 5:
        return "🟢 OKAZJA"
    else:
        return "⚪ zwykłe"


# -------- GŁÓWNY BOT --------
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

                title = ad.get_text(" ", strip=True)

                if not is_ok(title):
                    continue

                price = get_price_from_page(link)

                score = score_deal(title, price)
                label = classify(score)

                msg = f"{label}\n🆕 {title}\n"

                if price:
                    msg += f"💰 {price} PLN\n"
                else:
                    msg += "💰 brak ceny\n"

                msg += f"⭐ score: {score}\n"
                msg += link

                # 🔥 tylko coś sensownego wysyłamy
                if score >= 3:
                    send(msg)

                seen.add(link)

                count += 1

                if count >= 4:
                    break

    save_seen(seen)


if __name__ == "__main__":
    run()
