"""
Dashboard 6: Review Analytics
Natural Language Processing (NLP), WordCloud visualization, keyword frequency, and sentiment classification
"""

import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False
from utils.ui_components import (
    apply_theme,
    render_page_header,
    render_kpi_card,
    render_sidebar_filters
)
from utils.visualizations import (
    plot_top_review_words,
    plot_sentiment_doughnut,
    plot_review_volume_by_destination,
    apply_pbi_theme
)

st.set_page_config(
    page_title="Review Analytics - India Tourism BI",
    page_icon="💬",
    layout="wide"
)

apply_theme()
filtered_df = render_sidebar_filters()

render_page_header(
    title="Tourist Review & Text Analytics",
    subtitle=(
        "Review themes and "
        + ("VADER sentiment analysis" if HAS_VADER else "rule-based keyword sentiment")
        + " across the selected records"
    ),
    badge="POWER BI DASHBOARD 6 • NLP & REVIEWS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# REAL VADER SENTIMENT CLASSIFICATION (WITH LEXICON FALLBACK)
# -------------------------------------------------------------
if not HAS_VADER:
    st.info("VADER is unavailable, so sentiment uses a simple keyword-count rule. Treat these scores as a rough text signal, not a nuanced sentiment measure.")

@st.cache_data
def compute_sentiment_scores(reviews_series):
    if HAS_VADER:
        analyzer = SentimentIntensityAnalyzer()
        sentiments = []
        compound_scores = []
        for r in reviews_series:
            text = str(r) if pd.notna(r) else ""
            scores = analyzer.polarity_scores(text)
            comp = scores['compound']
            compound_scores.append(comp)
            if comp >= 0.05:
                sentiments.append("Positive")
            elif comp <= -0.05:
                sentiments.append("Negative")
            else:
                sentiments.append("Neutral")
        return sentiments, compound_scores
    else:
        pos_words = {'great', 'good', 'excellent', 'amazing', 'wonderful', 'beautiful', 'awesome', 'best',
                     'loved', 'love', 'fantastic', 'nice', 'pleasant', 'superb', 'peaceful', 'stunning',
                     'breathtaking', 'memorable', 'clean', 'scenic', 'rich', 'must-visit', 'charming', 'worth'}
        neg_words = {'bad', 'poor', 'terrible', 'horrible', 'worst', 'dirty', 'crowded', 'expensive',
                     'disappointed', 'disappointing', 'rude', 'noisy', 'overrated', 'avoid', 'unpleasant'}
        sentiments = []
        compound_scores = []
        for r in reviews_series:
            text = str(r).lower() if pd.notna(r) else ""
            tokens = set(text.split())
            pos_cnt = len(tokens.intersection(pos_words))
            neg_cnt = len(tokens.intersection(neg_words))
            diff = pos_cnt - neg_cnt
            if diff > 0:
                comp = min(1.0, 0.25 + 0.15 * diff)
                sentiment = "Positive"
            elif diff < 0:
                comp = max(-1.0, -0.25 - 0.15 * abs(diff))
                sentiment = "Negative"
            else:
                comp = 0.0
                sentiment = "Neutral"
            compound_scores.append(round(comp, 3))
            sentiments.append(sentiment)
        return sentiments, compound_scores

analysis_df = filtered_df.copy()
analysis_df['Sentiment'], analysis_df['Polarity_Score'] = compute_sentiment_scores(analysis_df['Review'])

total_reviews = len(analysis_df)
pos_cnt = int((analysis_df['Sentiment'] == 'Positive').sum())
neu_cnt = int((analysis_df['Sentiment'] == 'Neutral').sum())
neg_cnt = int((analysis_df['Sentiment'] == 'Negative').sum())

if total_reviews > 0:
    pos_pct = round(pos_cnt / total_reviews * 100, 1)
    neu_pct = round(neu_cnt / total_reviews * 100, 1)
    if neg_cnt == 0:
        neg_pct = 0.0
        neu_pct = round(100.0 - pos_pct, 1)
    else:
        neg_pct = round(100.0 - pos_pct - neu_pct, 1)
else:
    pos_pct = neu_pct = neg_pct = 0.0

avg_polarity = round(analysis_df['Polarity_Score'].mean(), 3) if not analysis_df.empty else 0.0
score_label = "VADER Compound" if HAS_VADER else "Rule-based Score"
positive_rule = f"{pos_cnt:,} reviews (≥ +0.05)" if HAS_VADER else f"{pos_cnt:,} reviews (positive rule)"
neutral_rule = f"{neu_cnt:,} reviews (-0.05 to +0.05)" if HAS_VADER else f"{neu_cnt:,} reviews (neutral rule)"
negative_rule = f"{neg_cnt:,} reviews (≤ -0.05)" if HAS_VADER else f"{neg_cnt:,} reviews (negative rule)"

# -------------------------------------------------------------
# REVIEW KPIS (5 CARDS)
# -------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Total Review Records", f"{total_reviews:,}", "Active filtered sample", "#0284c7", "💬")
with c2:
    render_kpi_card("Positive Sentiment", f"{pos_pct:.1f}%", positive_rule, "#10b981", "😊")
with c3:
    render_kpi_card("Neutral Sentiment", f"{neu_pct:.1f}%", neutral_rule, "#6366f1", "😐")
with c4:
    render_kpi_card("Negative Sentiment", f"{neg_pct:.1f}%", negative_rule, "#ef4444", "🙁")
with c5:
    render_kpi_card(f"Average {score_label}", f"{avg_polarity:+0.3f}", "Score range: -1 to +1", "#f97316", "📊")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ROW 2: WORD FREQUENCY & VADER DOUGHNUT
# -------------------------------------------------------------
col_words, col_doughnut = st.columns([1.35, 1.0])

with col_words:
    st.plotly_chart(plot_top_review_words(analysis_df, top_n=10), use_container_width=True)

with col_doughnut:
    st.plotly_chart(plot_sentiment_doughnut(analysis_df), use_container_width=True)

# -------------------------------------------------------------
# ROW 3: REVIEW COUNT BY DESTINATION
# -------------------------------------------------------------
st.plotly_chart(plot_review_volume_by_destination(analysis_df, top_n=10), use_container_width=True)

# -------------------------------------------------------------
# INTERACTIVE REVIEW SEARCH ENGINE
# -------------------------------------------------------------
st.markdown("""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); border-top: 4px solid #0284c7;">
    <h3 style="margin: 0 0 6px 0; font-size: 17px; font-weight: 700; color: #0f172a;">
        🔍 Interactive Tourist Review Explorer
    </h3>
    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Filter by destination or search specific visitor keywords (e.g., 'pleasant', 'crowded', 'photography', 'clean').
    </p>
""", unsafe_allow_html=True)

search_col1, search_col2 = st.columns([1, 1.5])

with search_col1:
    places_list = ["All Destinations"] + sorted(analysis_df['Place'].unique().tolist())
    selected_place = st.selectbox("Select Destination", places_list)

with search_col2:
    search_keyword = st.text_input("Search Review Text", placeholder="Type a keyword to filter reviews...")

matched_reviews = analysis_df.copy()
if selected_place != "All Destinations":
    matched_reviews = matched_reviews[matched_reviews['Place'] == selected_place]
if search_keyword.strip():
    matched_reviews = matched_reviews[matched_reviews['Review'].str.contains(search_keyword, case=False, na=False)]

st.markdown(f"**Found {len(matched_reviews):,} matching reviews**")

if not matched_reviews.empty:
    display_reviews = matched_reviews[['Visitor_ID', 'Place', 'State', 'Rating', 'Sentiment', 'Polarity_Score', 'Review']].copy()
    display_reviews['Polarity_Score'] = display_reviews['Polarity_Score'].round(3)
    display_reviews = display_reviews.rename(columns={'Polarity_Score': score_label})
    st.dataframe(display_reviews, use_container_width=True, height=280)
else:
    st.info("No reviews matched your search keyword.")

st.markdown("</div>", unsafe_allow_html=True)

