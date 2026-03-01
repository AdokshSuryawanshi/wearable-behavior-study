"""
Recovery Tracking & Behavior Change Project
Phase 3: Visualisation
Reads outputs from 02_analysis.py and saves charts to /charts/
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

# ── SETUP ─────────────────────────────────────────────────────────────────────

os.makedirs("charts", exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
COLORS = sns.color_palette("muted", 8)

df         = pd.read_csv("analysed_data.csv")
kw_df      = pd.read_csv("keyword_counts.csv")
theme_df   = pd.read_csv("theme_counts.csv")

df["full_text"] = df["full_text"].fillna("")

THEME_LABELS = {
    "acted_on_score":      "Acted on Score",
    "awareness_no_action": "Awareness, No Action",
    "behavior_change":     "Behaviour Change",
    "friction_barriers":   "Friction / Barriers",
    "anxiety_obsession":   "Anxiety / Obsession",
    "positive_impact":     "Positive Impact",
    "skeptical":           "Skeptical",
    "unclassified":        "Unclassified",
}

print("=" * 55)
print("Recovery Tracking Research -- Visualisation")
print("=" * 55)

# ── CHART 1: Theme Frequency Bar ──────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
td = theme_df[theme_df["theme"] != "unclassified"].copy()
td["label"] = td["theme"].map(THEME_LABELS)
td = td.sort_values("count", ascending=True)
bars = ax.barh(td["label"], td["count"], color=COLORS[:len(td)], edgecolor="white")
ax.bar_label(bars, padding=4, fontsize=10)
ax.set_xlabel("Number of posts / comments", fontsize=11)
ax.set_title("Behavioural Themes in Recovery Tracking Discussions", fontsize=13, fontweight="bold", pad=12)
ax.xaxis.set_major_locator(ticker.MultipleLocator(25))
plt.tight_layout()
plt.savefig("charts/01_theme_frequency.png", dpi=150)
plt.close()
print("Saved: charts/01_theme_frequency.png")

# ── CHART 2: Sentiment by Subreddit (stacked bar) ─────────────────────────────

fig, ax = plt.subplots(figsize=(8, 5))
sentiment_order = ["positive", "neutral", "negative"]
sent_colors     = ["#5aac6e", "#aaaaaa", "#e05c5c"]
sent_pivot = (
    df.groupby(["subreddit", "sentiment"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=sentiment_order, fill_value=0)
)
sent_pivot.plot(kind="bar", stacked=True, ax=ax, color=sent_colors,
                edgecolor="white", width=0.6)
ax.set_xlabel("")
ax.set_ylabel("Number of posts / comments", fontsize=11)
ax.set_title("Sentiment Distribution by Subreddit", fontsize=13, fontweight="bold", pad=12)
ax.legend(title="Sentiment", loc="upper right", fontsize=9)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11)
plt.tight_layout()
plt.savefig("charts/02_sentiment_by_subreddit.png", dpi=150)
plt.close()
print("Saved: charts/02_sentiment_by_subreddit.png")

# ── CHART 3: Top Keywords ─────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
kw = kw_df.head(15).sort_values("count", ascending=True)
bars = ax.barh(kw["keyword"], kw["count"], color=COLORS[1], edgecolor="white")
ax.bar_label(bars, padding=4, fontsize=10)
ax.set_xlabel("Mentions", fontsize=11)
ax.set_title("Top Keywords Across All Posts & Comments", fontsize=13, fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig("charts/03_keyword_frequency.png", dpi=150)
plt.close()
print("Saved: charts/03_keyword_frequency.png")

# ── CHART 4: Theme x Subreddit Heatmap ───────────────────────────────────────

theme_by_sub = (
    df["theme_str"].str.split("|").explode()
    .rename("theme")
    .to_frame()
    .join(df["subreddit"])
    .groupby(["subreddit", "theme"])
    .size()
    .unstack(fill_value=0)
)
theme_by_sub = theme_by_sub.drop(columns=["unclassified"], errors="ignore")
theme_by_sub.columns = [THEME_LABELS.get(c, c) for c in theme_by_sub.columns]

fig, ax = plt.subplots(figsize=(10, 4))
sns.heatmap(theme_by_sub, annot=True, fmt="d", cmap="YlOrRd",
            linewidths=0.5, linecolor="white", ax=ax, cbar_kws={"label": "Count"})
ax.set_title("Behavioural Theme Frequency by Subreddit", fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("")
ax.set_xlabel("")
plt.xticks(rotation=30, ha="right", fontsize=9)
plt.tight_layout()
plt.savefig("charts/04_theme_heatmap.png", dpi=150)
plt.close()
print("Saved: charts/04_theme_heatmap.png")

# ── CHART 5: Acted-on vs Ignored Score comparison ────────────────────────────

fig, ax = plt.subplots(figsize=(7, 4))
compare = (
    df["theme_str"].str.split("|").explode()
    .rename("theme")
    .to_frame()
    .join(df["subreddit"])
    .query("theme in ['acted_on_score', 'awareness_no_action']")
    .groupby(["subreddit", "theme"])
    .size()
    .unstack(fill_value=0)
    .rename(columns={"acted_on_score": "Acted on Score", "awareness_no_action": "Awareness, No Action"})
)
compare.plot(kind="bar", ax=ax, color=["#5aac6e", "#e05c5c"],
             edgecolor="white", width=0.6)
ax.set_xlabel("")
ax.set_ylabel("Count", fontsize=11)
ax.set_title("Acted on Score vs. Ignored Score by Subreddit", fontsize=13, fontweight="bold", pad=12)
ax.legend(fontsize=10)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11)
plt.tight_layout()
plt.savefig("charts/05_acted_vs_ignored.png", dpi=150)
plt.close()
print("Saved: charts/05_acted_vs_ignored.png")

# ── DONE ──────────────────────────────────────────────────────────────────────

print("\n" + "=" * 55)
print("DONE -- 5 charts saved to /charts/")
print("=" * 55)
