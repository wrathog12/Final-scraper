import feedparser
import time
import hashlib
from datetime import datetime, timedelta

# --------------- CONFIG ---------------
CRIME_KEYWORDS = [
    "murder", "rape", "robbery", "assault", "shootout", "snatching", "theft", "kidnapping", "gang war",
    "sexual assault", "stabbing", "molestation", "burglary", "chain snatching", "acid attack",
    "domestic violence", "child abuse", "attempt to murder", "gangrape", "human trafficking",
    "cyber crime", "hit and run", "road rage", "terror plot", "illegal arms", "extortion",
    "drug seizure", "drug trafficking", "illegal betting", "crime syndicate", "dowry death",
    "honour killing", "ATM robbery", "carjacking", "cattle theft", "public violence",
    "fake encounter", "custodial death", "missing child", "police brutality"
]

MAX_PER_KEYWORD = 2  # max entries per keyword
BASE_URL = "https://news.google.com/rss/search?q="
DELHI_QUERY_FORMAT = "Delhi+{}"
seen_hashes = set()

# --------------- TIME WINDOW SETUP ---------------
to_date = datetime.utcnow().date()
from_date = to_date - timedelta(days=5)

# --------------- UTILITY ---------------
def dedup(title, link):
    h = hashlib.md5((title + link).encode()).hexdigest()
    if h in seen_hashes:
        return False
    seen_hashes.add(h)
    return True

# --------------- MAIN FUNCTION ---------------
def fetch_news():
    from datetime import datetime, timedelta
    import time
    import feedparser
    # ... (your variable setup: CRIME_KEYWORDS, BASE_URL, etc.) ...

    news_items = []
    total = 0

    for crime in CRIME_KEYWORDS:
        query = DELHI_QUERY_FORMAT.format(crime.replace(" ", "+"))
        url = BASE_URL + query
        feed = feedparser.parse(url)

        count = 0
        for entry in feed.entries:
            # Check date within 5-day window
            if hasattr(entry, 'published_parsed'):
                published_date = datetime(*entry.published_parsed[:6]).date()
                if not (from_date <= published_date <= to_date):
                    continue
            else:
                continue

            if dedup(entry.title, entry.link):
                total += 1
                count += 1

                news_items.append({
                    "title": entry.title,
                    "date": entry.published,  # Use entry.published (string) or format as needed
                    "url": entry.link
                })

            if count >= MAX_PER_KEYWORD:
                break

        time.sleep(0.2)  # friendly delay

    return news_items

# --------------- RUN ---------------
if __name__ == "__main__":
    results = fetch_news()
    print(f"\nFetched {len(results)} unique headlines.\n")
    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['title']}")
        print(f" {item['date']}")
        print(f" {item['url']}\n")
