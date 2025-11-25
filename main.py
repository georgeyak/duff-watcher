import json
import time
import requests
import feedparser
import os

REDDIT_FEED = "https://www.reddit.com/r/TorontoTickets/new/.rss"
KEYWORDS = ["hilary", "duff", "hilary duff"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": False}
    requests.post(url, data=data)

def load_seen():
    try:
        with open("seen.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open("seen.json", "w") as f:
        json.dump(list(seen), f)

def check_reddit():
    feed = feedparser.parse(REDDIT_FEED)
    seen = load_seen()
    new_seen = False

    for entry in feed.entries:
        title = entry.title.lower()
        link = entry.link
        post_id = entry.id

        if post_id in seen:
            continue

        if any(keyword in title for keyword in KEYWORDS):
            msg = f"🎟 NEW Hilary Duff Ticket Post\n\nTitle: {entry.title}\nLink: {link}"
            send_telegram(msg)
            new_seen = True

        seen.add(post_id)

    if new_seen:
        save_seen(seen)

if __name__ == "__main__":
    check_reddit()
