"""
Recovery Tracking & Behavior Change Project
Phase 3: Analysis v2 — improved pattern matching
Run from same folder as raw_data.csv
"""

import pandas as pd
import re
from collections import Counter

df = pd.read_csv("raw_data.csv")
df["full_text"] = df["full_text"].fillna("").str.lower()
df["title"]     = df["title"].fillna("").str.lower()
df["text"]      = df["text"].fillna("").str.lower()

print("=" * 55)
print("Recovery Tracking Research -- Analysis v2")
print("=" * 55)
print(f"\nLoaded {len(df)} items")
print(df["subreddit"].value_counts().to_string())

THEMES = {
    "acted_on_score": [
        r"took a rest day", r"rest day because", r"skipped.*work", r"backed off",
        r"dialed back", r"eased up", r"reduced.*intensity", r"adjusted.*training",
        r"adjusted.*sleep", r"changed.*workout", r"score told me", r"score said",
        r"recovery said", r"readiness said", r"listened to.*body", r"listened to.*score",
        r"followed.*score", r"trusted.*score", r"acted on.*score", r"decided to rest",
        r"so i rested", r"made.*adjustment", r"made some changes", r"incorporated",
        r"started journaling", r"stopped.*alcohol", r"stopped.*drink", r"added.*sleep",
        r"improved.*sleep", r"sleep consistency", r"eye.?opening", r"wake up.*check",
        r"check.*recovery",
    ],
    "awareness_no_action": [
        r"just (watch|look at|check|monitor|track)", r"don.t (act|do anything|change|adjust)",
        r"doesn.t (change|affect|impact|influence) (what|how|my|anything)",
        r"ignor.* (score|recovery|readiness|data)", r"stopped.*caring", r"stopped.*checking",
        r"don.t care.*score", r"don.t look", r"not helpful", r"getting any real value",
        r"wondering if i.m getting", r"what.s the point", r"not sure.*worth", r"is it worth",
        r"not acting", r"just information", r"train anyway", r"workout anyway",
        r"go anyway", r"regardless of.*score", r"regardless of.*recovery",
    ],
    "behavior_change": [
        r"changed my", r"change.*habit", r"habit.*change",
        r"now i (always|usually|try|make sure|go)", r"started to", r"began to",
        r"helped me (realise|realize|understand|see|notice)", r"realised i", r"realized i",
        r"more (aware|mindful|conscious|intentional)", r"pay (more )?attention",
        r"changed how i", r"different approach", r"better habits", r"new habit",
        r"sleep better", r"recovering better", r"performing better",
        r"seeing improvement", r"seen improvement", r"noticed improvement",
        r"made a difference", r"made me more", r"some changes", r"lifestyle change",
        r"routine.*changed",
    ],
    "skeptical": [
        r"not accurate", r"inaccurate", r"wrong.*score", r"score.*wrong",
        r"doesn.t reflect", r"not reliable", r"unreliable", r"garbage", r"snake oil",
        r"placebo", r"gimmick", r"waste of money", r"don.t trust", r"can.t trust",
        r"skeptic", r"bullshit", r"not (sure|convinced)", r"forgotten my personal",
        r"seems off", r"feels off", r"doesn.t make sense", r"confused by",
        r"plummeted.*feel.*good", r"feel good.*low score", r"low.*feel fine",
    ],
    "positive_impact": [
        r"game.?changer", r"love.*score", r"love it", r"really helpful", r"so helpful",
        r"best.*purchase", r"highly recommend", r"worth it", r"accurate", r"spot on",
        r"feels right", r"trust.*data", r"data.*accurate", r"motivated",
        r"pushed me", r"helped me", r"made me better",
    ],
    "anxiety_obsession": [
        r"obsess", r"anxious.*score", r"score.*anxious", r"stress.*score", r"score.*stress",
        r"can.t stop checking", r"check.*every", r"addicted", r"too much", r"paranoid",
        r"overthink", r"unhealthy", r"slave to.*score", r"let.*score.*decide",
        r"nervous.*score", r"disappoint.*score", r"green.*excited", r"red.*devastated",
    ],
    "friction_barriers": [
        r"don.t know (what|how) to", r"confusing", r"too (complex|complicated|much data)",
        r"overwhelm", r"no.*time", r"can.t.*rest", r"have to.*work", r"have to.*train",
        r"can.t.*skip", r"but i (still|had to|needed to)", r"even though.*score",
        r"despite.*score", r"no actionable", r"what should i (do|change)",
        r"how do i improve", r"how to improve.*hrv", r"what.*improve",
    ],
}

def match_themes(text):
    matched = []
    for theme, patterns in THEMES.items():
        for pat in patterns:
            if re.search(pat, text):
                matched.append(theme)
                break
    return matched if matched else ["unclassified"]

df["themes"]    = df["full_text"].apply(match_themes)
df["theme_str"] = df["themes"].apply(lambda x: "|".join(x))

KEYWORDS = [
    "recovery score", "hrv", "readiness", "rest day", "strain",
    "sleep score", "habit", "behavior", "changed", "ignore",
    "useless", "accurate", "anxiety", "obsess", "aware",
    "adjusted", "skipped", "listened", "trust", "skeptic",
    "motivated", "journal", "routine", "lifestyle",
]

kw_counts = {kw: df["full_text"].str.contains(kw, regex=False).sum() for kw in KEYWORDS}
kw_df = pd.DataFrame(list(kw_counts.items()), columns=["keyword", "count"])
kw_df = kw_df.sort_values("count", ascending=False).reset_index(drop=True)

POS_WORDS = ["helpful", "love", "great", "accurate", "worth", "changed", "better",
             "improved", "recommend", "good", "useful", "valuable", "motivated",
             "consistent", "reliable"]
NEG_WORDS = ["useless", "wrong", "inaccurate", "garbage", "waste", "bad", "terrible",
             "broken", "annoying", "misleading", "anxious", "obsess", "stress",
             "paranoid", "meaningless", "ignore", "confused", "disappointed", "frustrated"]

def simple_sentiment(text):
    pos = sum(1 for w in POS_WORDS if w in text)
    neg = sum(1 for w in NEG_WORDS if w in text)
    if pos > neg: return "positive"
    elif neg > pos: return "negative"
    else: return "neutral"

df["sentiment"] = df["full_text"].apply(simple_sentiment)

all_themes   = [t for sublist in df["themes"] for t in sublist]
theme_counts = Counter(all_themes)
theme_df     = pd.DataFrame(theme_counts.most_common(), columns=["theme", "count"])

sentiment_by_sub = df.groupby(["subreddit", "sentiment"]).size().unstack(fill_value=0)

theme_by_sub = (
    df.explode("themes")
    .groupby(["subreddit", "themes"])
    .size()
    .unstack(fill_value=0)
)

top_posts = (
    df.sort_values("score", ascending=False)
    .groupby("theme_str")
    .head(2)[["subreddit", "theme_str", "sentiment", "score", "title", "url"]]
    .reset_index(drop=True)
)

df.to_csv("analysed_data.csv", index=False, encoding="utf-8")
kw_df.to_csv("keyword_counts.csv", index=False)
theme_df.to_csv("theme_counts.csv", index=False)
top_posts.to_csv("top_posts_by_theme.csv", index=False, encoding="utf-8")

print("\n-- THEME BREAKDOWN --")
print(theme_df.to_string(index=False))

classified = (df["theme_str"] != "unclassified").sum()
print(f"\n-- CLASSIFICATION RATE --")
print(f"Classified: {classified} / {len(df)} ({classified/len(df)*100:.1f}%)")

print("\n-- KEY THEMES (research question) --")
for t in ["acted_on_score", "awareness_no_action", "behavior_change", "friction_barriers"]:
    n = df["theme_str"].str.contains(t, na=False).sum()
    print(f"  {t}: {n}")

print("\n-- SENTIMENT --")
print(df["sentiment"].value_counts().to_string())

print("\n-- SENTIMENT BY SUBREDDIT --")
print(sentiment_by_sub.to_string())

print("\n-- TOP KEYWORDS --")
print(kw_df.head(15).to_string(index=False))

print("\n" + "=" * 55)
print("DONE — Run 03_visualise.py next")
print("=" * 55)
