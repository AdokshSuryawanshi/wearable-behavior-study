"""
Recovery Tracking & Behavior Change Project
Phase 2: Data Collection
Uses Reddit public JSON API — no credentials needed
Run in Claude Code on your local machine
"""

import requests
import pandas as pd
import time

HEADERS = {"User-Agent": "Mozilla/5.0 (research project)"}

SUBREDDITS = ["whoop", "ouraring", "QuantifiedSelf", "Garmin"]

QUERIES = [
    "recovery score changed my",
    "HRV behavior habit",
    "readiness score actually",
    "sleep tracking changed",
    "recovery data useless",
    "don't act on my scores",
    "adjusted training recovery",
    "ignore my recovery score",
    "recovery tracking awareness",
    "wearable habit change"
]


def fetch_posts(subreddit, query, limit=25):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {"q": query, "sort": "relevance", "limit": limit, "t": "all", "restrict_sr": 1}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if r.status_code != 200:
            print(f"  [!] {subreddit} returned {r.status_code}")
            return []
        posts = []
        for item in r.json()["data"]["children"]:
            p = item["data"]
            posts.append({
                "source": "reddit_post",
                "subreddit": subreddit,
                "query_used": query,
                "title": p.get("title", ""),
                "text": p.get("selftext", ""),
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "url": "https://reddit.com" + p.get("permalink", ""),
                "created_utc": p.get("created_utc", 0)
            })
        return posts
    except Exception as e:
        print(f"  [!] Error: {e}")
        return []


def fetch_comments(subreddit, limit=100):
    url = f"https://www.reddit.com/r/{subreddit}/comments.json"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params={"limit": limit}, timeout=10)
        if r.status_code != 200:
            return []
        comments = []
        keywords = ["recovery", "hrv", "readiness", "sleep score", "rest day",
                    "strain", "habit", "changed", "ignore", "useless", "actually"]
        for item in r.json()["data"]["children"]:
            c = item["data"]
            body = c.get("body", "")
            if any(k in body.lower() for k in keywords):
                comments.append({
                    "source": "reddit_comment",
                    "subreddit": subreddit,
                    "query_used": "comments_feed",
                    "title": c.get("link_title", ""),
                    "text": body,
                    "score": c.get("score", 0),
                    "num_comments": 0,
                    "url": "https://reddit.com" + c.get("permalink", ""),
                    "created_utc": c.get("created_utc", 0)
                })
        return comments
    except Exception as e:
        print(f"  [!] Comment error: {e}")
        return []


# ── RUN ───────────────────────────────────────────────────────────────────────

all_data = []
seen_urls = set()

print("=" * 55)
print("Recovery Tracking Research — Data Collection")
print("=" * 55)

for sub in SUBREDDITS:
    print(f"\n-- r/{sub} --")
    for query in QUERIES:
        posts = fetch_posts(sub, query, limit=25)
        for p in posts:
            if p["url"] not in seen_urls:
                all_data.append(p)
                seen_urls.add(p["url"])
        time.sleep(1.5)

    comments = fetch_comments(sub, limit=100)
    for c in comments:
        if c["url"] not in seen_urls:
            all_data.append(c)
            seen_urls.add(c["url"])
    time.sleep(1.5)

    print(f"  {sum(1 for d in all_data if d['subreddit'] == sub)} items from r/{sub}")

df = pd.DataFrame(all_data)
df = df[df["text"].str.len() > 80].reset_index(drop=True)
df["full_text"] = df["title"] + " " + df["text"]
df.to_csv("raw_data.csv", index=False)

print("\n" + "=" * 55)
print(f"DONE — {len(df)} usable items")
print(df["subreddit"].value_counts().to_string())
print("\nSaved: raw_data.csv")
print("Next: Run 02_analysis.py")
print("=" * 55)
