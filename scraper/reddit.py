import praw

reddit = praw.Reddit(
    client_id="BrBAYmRKblF8oAZMXTnRDw",
    client_secret="QwH4bejg_edcMd1JpH8TZNN4vHIGgA",
    user_agent="DelhiCrimeScraper by u/Heavy-Use7287"
)

SEARCH_KEYWORDS = ["Delhi crime"," Delhi crime news","Delhi Case", "Delhi murder", "Delhi robbery","Delhi theft"]
CRIME_FILTER_KEYWORDS = ["crime", "murder", "theft", "violence", "police", "FIR", "kidnap"]

def fetch_reddit_news():
    results = []
    try:
        subreddit = reddit.subreddit("Delhi")
        for keyword in SEARCH_KEYWORDS:
            for post in subreddit.search(keyword, sort="new", limit=20):
                title_lower = post.title.lower()
                if any(crime_kw in title_lower for crime_kw in CRIME_FILTER_KEYWORDS):
                    results.append({
                        "title": post.title,
                        "url": post.url,
                        "score": post.score,
                        "created": post.created_utc,
                        "subreddit": "Delhi"
                    })
    except Exception as e:
        return [{"error": str(e)}]
    
    return results
