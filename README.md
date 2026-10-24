# App Review Insights: What Are Duolingo Users Complaining About?

**Using NLP to turn 240,000+ app reviews into product insights, and to spot which complaints are growing over time.**

> 🚧 **Status: in progress.** Data collection and exploration are done; AI labeling and the dashboard are next. See the [roadmap](#roadmap).

---

## The question

App stores collect thousands of reviews a day, far more than a product team can read. This project asks:

1. **What do users complain about most?** (e.g., ads, pricing, bugs, lesson design)
2. **Which complaints are growing?** A rising complaint is an early warning sign for churn.
3. **Can AI models sort reviews accurately?** Every model's labels are checked against hand-labeled reviews before I trust them.

## Data

| | |
|---|---|
| **Source** | Google Play Store, Duolingo (US, English reviews) |
| **Collected** | 242,675 reviews |
| **Period** | April 1 – October 22, 2026 |
| **Fields** | review text, star rating (1–5), date, app version, helpful votes |

**Privacy:** usernames and profile images were dropped during collection. Only the review content needed for analysis is kept. Raw data is not stored in this repo; run the collection script to rebuild it.

## Approach

```
Collect reviews  →  Clean & explore  →  Label sentiment  →  Label topics  →  Validate AI  →  Track trends  →  Dashboard
   (scraper)         (pandas)          (Hugging Face)     (zero-shot)     (hand labels)    (monthly)      (Streamlit)
```

1. **Collection:** paginated scraper with retry logic and exponential backoff to handle rate limiting; checkpoints save progress during long runs.
2. **Cleaning & exploration:** removed duplicates and empty reviews, flagged very short reviews (e.g., "good app"), checked weekly volume for data gaps, and found the most common phrases in 1-star vs. 5-star reviews to define the complaint topics.
3. **Sentiment & topics:** pretrained Hugging Face models label each review. Topics come from the exploration step, not guesswork.
4. **Validation:** model labels are compared with a hand-labeled sample (accuracy and confusion matrix).
5. **Trends:** monthly share of each complaint topic, using a sample of reviews per month to keep model costs manageable.
6. **Dashboard:** an interactive Streamlit app to explore topics, trends, and example reviews.

## Roadmap

- [x] Collect 6+ months of reviews with a robust scraper
- [x] Clean data and explore ratings, volume, and common phrases
- [ ] Label sentiment with a Hugging Face model
- [ ] Classify complaint topics (zero-shot)
- [ ] Validate model labels against a hand-labeled sample
- [ ] Measure which complaints are growing month over month
- [ ] Build and deploy the Streamlit dashboard

## Project structure

```
app-review-insights/
├── src/
│   └── collect_reviews.py          # collects reviews from Google Play
├── notebooks/
│   ├── 01_explore.ipynb            # first look at the data
│   └── 02_clean_explore.ipynb      # cleaning, ratings over time, top phrases
├── data/                           # not in repo (rebuild with the script)
├── requirements.txt
└── README.md
```

## How to run

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Collect reviews (about 40 minutes for 6 months of data)
python src/collect_reviews.py

# 3. Open the notebooks to clean and explore
jupyter notebook notebooks/
```

## Tools

Python · pandas · scikit-learn · matplotlib · google-play-scraper · Hugging Face Transformers *(next)* · Streamlit *(next)*
