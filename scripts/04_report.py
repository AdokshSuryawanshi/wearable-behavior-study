"""
Recovery Tracking & Behavior Change Project
Phase 4: Report Generation
Builds a self-contained HTML report from all prior outputs
"""

import pandas as pd
import base64, os, textwrap
from datetime import datetime

# ── LOAD ──────────────────────────────────────────────────────────────────────

df         = pd.read_csv("analysed_data.csv")
kw_df      = pd.read_csv("keyword_counts.csv")
theme_df   = pd.read_csv("theme_counts.csv")
top_posts  = pd.read_csv("top_posts_by_theme.csv")

df["text"]      = df["text"].fillna("")
df["title"]     = df["title"].fillna("")
df["theme_str"] = df["theme_str"].fillna("unclassified")

THEME_LABELS = {
    "acted_on_score":    "Acted on Score",
    "anxiety_obsession": "Anxiety / Obsession",
    "changed_behaviour": "Changed Behaviour",
    "ignored_score":     "Ignored Score",
    "positive_impact":   "Positive Impact",
    "skeptical":         "Skeptical",
    "unclassified":      "Unclassified",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def img_tag(path, alt="chart", width="100%"):
    if not os.path.exists(path):
        return f'<p style="color:#999">[Chart not found: {path}]</p>'
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{b64}" alt="{alt}" style="width:{width};border-radius:6px;box-shadow:0 1px 6px #0002">'

def df_to_html(d, max_rows=None):
    if max_rows:
        d = d.head(max_rows)
    return d.to_html(index=False, border=0, classes="data-table")

# ── SUMMARY STATS ─────────────────────────────────────────────────────────────

total          = len(df)
n_posts        = (df["source"] == "reddit_post").sum()
n_comments     = (df["source"] == "reddit_comment").sum()
subreddits     = df["subreddit"].nunique()
sentiment_pct  = df["sentiment"].value_counts(normalize=True).mul(100).round(1)
top_theme      = theme_df[theme_df["theme"] != "unclassified"].iloc[0]
date_str       = datetime.now().strftime("%d %B %Y")

# Top 3 example posts per key theme
def get_examples(theme_key, n=3):
    mask = df["theme_str"].str.contains(theme_key, na=False)
    sample = df[mask].sort_values("score", ascending=False).head(n)
    rows = ""
    for _, row in sample.iterrows():
        title = row["title"].strip().capitalize()[:120]
        snippet = row["text"].strip()[:200].replace("\n", " ")
        url = row["url"]
        sub = row["subreddit"]
        score = int(row["score"])
        rows += f"""
        <div class="example-card">
          <div class="ex-meta">r/{sub} &nbsp;|&nbsp; {score} upvotes</div>
          <a href="{url}" target="_blank" class="ex-title">{title}</a>
          <p class="ex-snippet">{snippet}{"..." if len(row["text"]) > 200 else ""}</p>
        </div>"""
    return rows

# ── PRE-COMPUTE TABLE HTML ────────────────────────────────────────────────────

theme_table_df = theme_df.copy()
theme_table_df["theme"] = theme_table_df["theme"].map(lambda x: THEME_LABELS.get(x, x))
theme_table_df.columns = ["Theme", "Count"]
theme_table_html = df_to_html(theme_table_df)

kw_table_df = kw_df.head(15).copy()
kw_table_df.columns = ["Keyword", "Mentions"]
kw_table_html = df_to_html(kw_table_df)

# ── BUILD HTML ────────────────────────────────────────────────────────────────

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recovery Tracking Research Report</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f4f6f9; color: #1a1a2e; line-height: 1.6;
    }}
    header {{
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
      color: white; padding: 48px 40px 40px;
    }}
    header h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 8px; }}
    header p  {{ opacity: 0.75; font-size: 1rem; }}
    .badge {{
      display: inline-block; background: rgba(255,255,255,0.15);
      border-radius: 20px; padding: 3px 12px; font-size: 0.82rem;
      margin-top: 14px; margin-right: 6px;
    }}
    main {{ max-width: 1060px; margin: 0 auto; padding: 36px 24px 60px; }}
    h2 {{
      font-size: 1.3rem; font-weight: 700; margin: 48px 0 16px;
      padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; color: #0f3460;
    }}
    h3 {{ font-size: 1.05rem; font-weight: 600; margin: 28px 0 10px; color: #333; }}
    p  {{ margin-bottom: 12px; color: #444; }}

    /* Stat cards */
    .stats {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 24px 0; }}
    .stat-card {{
      flex: 1; min-width: 140px; background: white; border-radius: 10px;
      padding: 20px 22px; box-shadow: 0 1px 4px #0001;
      border-top: 3px solid #0f3460;
    }}
    .stat-card .num {{ font-size: 2rem; font-weight: 700; color: #0f3460; }}
    .stat-card .lbl {{ font-size: 0.82rem; color: #888; margin-top: 2px; }}

    /* Charts */
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
    .chart-box  {{
      background: white; border-radius: 10px; padding: 18px;
      box-shadow: 0 1px 4px #0001;
    }}
    .chart-box.full {{ grid-column: 1 / -1; }}
    .chart-box p.cap {{ font-size: 0.8rem; color: #999; margin-top: 8px; text-align: center; }}

    /* Tables */
    .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    .data-table th {{
      background: #0f3460; color: white; padding: 9px 12px;
      text-align: left; font-weight: 600;
    }}
    .data-table td {{ padding: 8px 12px; border-bottom: 1px solid #eee; color: #333; }}
    .data-table tr:hover td {{ background: #f8faff; }}
    .table-wrap {{ background: white; border-radius: 10px; overflow: hidden;
                  box-shadow: 0 1px 4px #0001; margin: 16px 0; }}

    /* Example cards */
    .example-card {{
      background: white; border-radius: 8px; padding: 14px 16px;
      margin-bottom: 12px; box-shadow: 0 1px 3px #0001;
      border-left: 3px solid #0f3460;
    }}
    .ex-meta    {{ font-size: 0.75rem; color: #999; margin-bottom: 4px; }}
    .ex-title   {{ font-weight: 600; color: #0f3460; text-decoration: none; font-size: 0.95rem; }}
    .ex-title:hover {{ text-decoration: underline; }}
    .ex-snippet {{ font-size: 0.82rem; color: #666; margin-top: 6px; }}

    /* Sentiment pills */
    .pill {{
      display: inline-block; border-radius: 12px; padding: 2px 10px;
      font-size: 0.78rem; font-weight: 600;
    }}
    .pill.positive {{ background: #e6f9ee; color: #2e7d32; }}
    .pill.negative {{ background: #fdecea; color: #c62828; }}
    .pill.neutral  {{ background: #f0f0f0; color: #666; }}

    .finding-box {{
      background: #eef4ff; border-left: 4px solid #0f3460;
      border-radius: 6px; padding: 14px 18px; margin: 16px 0; font-size: 0.93rem;
    }}
    footer {{
      text-align: center; padding: 30px; color: #aaa; font-size: 0.8rem;
      border-top: 1px solid #e2e8f0; margin-top: 40px;
    }}
  </style>
</head>
<body>

<header>
  <h1>Recovery Tracking &amp; Behavior Change</h1>
  <p>Reddit Data Analysis &mdash; {date_str}</p>
  <span class="badge">r/whoop</span>
  <span class="badge">r/ouraring</span>
  <span class="badge">r/QuantifiedSelf</span>
  <span class="badge">r/Garmin</span>
</header>

<main>

<!-- OVERVIEW -->
<h2>Overview</h2>
<div class="stats">
  <div class="stat-card"><div class="num">{total}</div><div class="lbl">Total items</div></div>
  <div class="stat-card"><div class="num">{n_posts}</div><div class="lbl">Posts</div></div>
  <div class="stat-card"><div class="num">{n_comments}</div><div class="lbl">Comments</div></div>
  <div class="stat-card"><div class="num">{subreddits}</div><div class="lbl">Subreddits</div></div>
  <div class="stat-card"><div class="num">{sentiment_pct.get("positive", 0)}%</div><div class="lbl">Positive sentiment</div></div>
  <div class="stat-card"><div class="num">{sentiment_pct.get("negative", 0)}%</div><div class="lbl">Negative sentiment</div></div>
</div>

<div class="finding-box">
  <strong>Key finding:</strong> The most common coded theme (excluding unclassified) is
  <em>{THEME_LABELS.get(top_theme["theme"], top_theme["theme"])}</em>
  ({int(top_theme["count"])} items), suggesting that doubt and critical evaluation of
  recovery metrics is a dominant voice in these communities &mdash; yet overall sentiment
  skews positive ({sentiment_pct.get("positive", 0)}%), indicating coexistence of enthusiasm
  and scepticism.
</div>

<!-- THEMES -->
<h2>Behavioural Themes</h2>
<p>Each post or comment was coded against six behavioural themes using keyword pattern matching.
   Items could match multiple themes.</p>

<div class="chart-grid">
  <div class="chart-box full">
    {img_tag("charts/01_theme_frequency.png", "Theme frequency")}
    <p class="cap">Figure 1 &mdash; Frequency of behavioural themes across all coded items</p>
  </div>
  <div class="chart-box full">
    {img_tag("charts/04_theme_heatmap.png", "Theme heatmap")}
    <p class="cap">Figure 2 &mdash; Theme distribution by subreddit</p>
  </div>
</div>

<div class="table-wrap">
  {theme_table_html}
</div>

<!-- SENTIMENT -->
<h2>Sentiment</h2>
<div class="chart-grid">
  <div class="chart-box full">
    {img_tag("charts/02_sentiment_by_subreddit.png", "Sentiment by subreddit")}
    <p class="cap">Figure 3 &mdash; Sentiment distribution by subreddit (lexicon-based scoring)</p>
  </div>
</div>

<div class="finding-box">
  <strong>r/whoop</strong> shows the highest proportion of positive sentiment, while
  <strong>r/QuantifiedSelf</strong> and <strong>r/Garmin</strong> have more negative
  and neutral items, consistent with a more analytical, data-critical audience.
</div>

<!-- ACTED ON vs IGNORED -->
<h2>Acted on Score vs. Ignored Score</h2>
<div class="chart-grid">
  <div class="chart-box full">
    {img_tag("charts/05_acted_vs_ignored.png", "Acted vs Ignored")}
    <p class="cap">Figure 4 &mdash; Posts explicitly describing acting on vs. ignoring recovery scores</p>
  </div>
</div>

<div class="finding-box">
  <strong>Ignoring scores is far more commonly discussed than acting on them</strong> across
  all subreddits. This may reflect a &ldquo;I know I should rest but I won&rsquo;t&rdquo;
  pattern, or simply that ignoring scores is more salient/shareable than quietly following them.
</div>

<!-- KEYWORDS -->
<h2>Keyword Frequency</h2>
<div class="chart-grid">
  <div class="chart-box full">
    {img_tag("charts/03_keyword_frequency.png", "Keyword frequency")}
    <p class="cap">Figure 5 &mdash; Top 15 recovery-related keywords across all items</p>
  </div>
</div>

<div class="table-wrap">
  {kw_table_html}
</div>

<!-- EXAMPLE POSTS -->
<h2>Example Posts by Theme</h2>

<h3>Changed Behaviour</h3>
{get_examples("changed_behaviour")}

<h3>Skeptical</h3>
{get_examples("skeptical")}

<h3>Anxiety / Obsession</h3>
{get_examples("anxiety_obsession")}

<h3>Acted on Score</h3>
{get_examples("acted_on_score")}

</main>

<footer>
  Generated by 04_report.py &mdash; Recovery Tracking &amp; Behavior Change Research &mdash; {date_str}
</footer>

</body>
</html>"""

# ── SAVE ──────────────────────────────────────────────────────────────────────

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("=" * 55)
print("Recovery Tracking Research -- Report")
print("=" * 55)
print(f"\nSaved: report.html")
print(f"Open it in any browser to view the full report.")
print("=" * 55)
