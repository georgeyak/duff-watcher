import json
import requests
import feedparser
import os

# Watch both subreddits
FEEDS = [
    "https://www.reddit.com/r/TorontoTickets/new/.rss",
    "https://www.reddit.com/r/gtamarketplace/new/.rss",
]

# Match either spelling; you can trim this if you want stricter matches
KEYWORDS = ["hilary", "hillary", "duff", "hilary duff", "hillary duff"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEEN_PATH = "seen.json"

def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[WARN] Missing TELEGRAM_* envs; dry-run:\n" + message)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": False}
    r = requests.post(url, data=data, timeout=20)
    r.raise_for_status()

def load_seen():
    try:
        with open(SEEN_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_seen(seen):
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f)

def title_matches(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)

def subreddit_from_entry(entry) -> str:
    # Try to infer subreddit (most reliable from the link)
    link = getattr(entry, "link", "") or ""
    # e.g., https://www.reddit.com/r/gtamarketplace/comments/xxxx/...
    try:
        parts = link.split("/r/")[1].split("/")[0]
        return parts
    except Exception:
        return "unknown"

def check_feeds():
    seen = load_seen()
    new_seen = False
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for e in feed.entries:
            eid = getattr(e, "id", None) or getattr(e, "link", None)
            if not eid or eid in seen:
                continue

            title = getattr(e, "title", "") or ""
            link = getattr(e, "link", "") or ""

            if title_matches(title):
                sub = subreddit_from_entry(e)
                msg = (
                    "🎟 NEW post mentioning Hilary/Hillary/Duff\n"
                    f"Subreddit: r/{sub}\n"
                    f"Title: {title}\n"
                    f"Link: {link}"
                )
                send_telegram(msg)
                print(f"[sent] r/{sub} :: {title}")
                new_seen = True

            # mark as seen regardless, so we don't reprocess this ID
            seen.add(eid)

    if new_seen:
        save_seen(seen)

if __name__ == "__main__":
    check_feeds()
