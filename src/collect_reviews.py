"""
Collect Google Play reviews for Duolingo, going back to START_DATE.
Run from anywhere:  python src/collect_reviews.py
"""
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

# ---------- Paths (work no matter which folder the terminal is in) ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # src/ -> app-review-insights/
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)                           # create data/ if missing

OUTPUT = DATA_DIR / "reviews_raw.csv"
CHECKPOINT = DATA_DIR / "reviews_checkpoint.csv"

# ---------- Settings ----------
APP_ID = "com.duolingo"
START_DATE = pd.Timestamp("2026-04-01")   # collect back to this date
MAX_REVIEWS = 300000                      # safety limit
BATCH_SIZE = 200                          # max reviews per request
MAX_RETRIES = 5                           # retries on an empty batch

# ---------- Collect ----------
all_reviews = []
token = None
retries = 0

while len(all_reviews) < MAX_REVIEWS:
    try:
        batch, new_token = reviews(
            APP_ID,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=BATCH_SIZE,
            continuation_token=token,
        )
    except Exception as e:                    # network hiccup, timeout, etc.
        print(f"Error: {e}")
        batch, new_token = [], token

    # Empty batch: wait and retry with the SAME token instead of quitting
    if not batch:
        retries += 1
        if retries > MAX_RETRIES:
            print("Still empty after several retries. Stopping.")
            break
        wait = 15 * retries                   # 15s, 30s, 45s, ... (backoff)
        print(f"Empty batch. Waiting {wait}s, retry {retries}/{MAX_RETRIES}...")
        time.sleep(wait)
        continue

    retries = 0                               # success: reset the counter
    token = new_token                         # only move the bookmark forward on success
    all_reviews.extend(batch)
    oldest = batch[-1]["at"]                  # newest-first, so the last one is the oldest

    if len(all_reviews) % 5000 == 0:
        print(f"Collected {len(all_reviews):,} reviews... now at {oldest:%Y-%m-%d}")

    if len(all_reviews) % 20000 == 0:         # checkpoint in case of a crash
        pd.DataFrame(all_reviews).to_csv(CHECKPOINT, index=False)

    if oldest < START_DATE:
        print(f"Reached {oldest:%Y-%m-%d}, past the start date. Stopping.")
        break

    time.sleep(1)                             # be polite to the server

# ---------- Clean up and save ----------
df = pd.DataFrame(all_reviews)

# Keep only what we need; drop usernames and profile pictures (privacy)
df = df[["reviewId", "content", "score", "thumbsUpCount", "at", "appVersion"]]
df = df.rename(columns={"content": "text", "score": "stars", "at": "date"})
df = df[df["date"] >= START_DATE]             # drop the few reviews from before the start date

df.to_csv(OUTPUT, index=False)

print("\nDone!")
print(f"Saved {len(df):,} reviews to {OUTPUT}")
print(f"Date range: {df['date'].min()}  to  {df['date'].max()}")