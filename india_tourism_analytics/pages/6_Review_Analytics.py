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
    generate_review_wordcloud,
    get_top_review_words,
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
    subtitle="Semantic text mining, WordCloud generation, keyword frequency distribution, and VADER sentiment classification",
    badge="POWER BI DASHBOARD 6 • NLP & REVIEWS"
)

if filtered_df.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust your sidebar filters.")
    st.stop()

# -------------------------------------------------------------
# REAL VADER SENTIMENT CLASSIFICATION (WITH LEXICON FALLBACK)
# -------------------------------------------------------------
if not HAS_VADER:
    st.info("💡 **Tip:** Install `vaderSentiment` via `pip install vaderSentiment` for advanced VADER sentiment scores. Currently running built-in sentiment classification.")

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

pos_pct = round((analysis_df['Sentiment'] == 'Positive').mean() * 100, 1)
neu_pct = round((analysis_df['Sentiment'] == 'Neutral').mean() * 100, 1)
neg_pct = round((analysis_df['Sentiment'] == 'Negative').mean() * 100, 1)
avg_polarity = round(analysis_df['Polarity_Score'].mean(), 3)

# -------------------------------------------------------------
# REVIEW KPIS
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Reviews", f"{len(analysis_df):,}", "Verified tourist logs", "#0284c7", "💬")
with c2:
    render_kpi_card("Positive Sentiment", f"{pos_pct}%", "VADER polarity >= +0.05", "#10b981", "😊")
with c3:
    render_kpi_card("Neutral / Moderate", f"{neu_pct}%", "Factual observations", "#6366f1", "😐")
with c4:
    render_kpi_card("Average Polarity", f"{avg_polarity:+0.3f}", "Scale: -1.0 to +1.0", "#f97316", "📊")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ROW 1: WORDCLOUD & FREQUENT WORDS
# -------------------------------------------------------------
col_wc, col_freq = st.columns([1.3, 1])

with col_wc:
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px 10px 18px; margin-bottom: 12px;">
        <div style="font-size: 15px; font-weight: 700; color: #0f172a;">☁️ Tourist Review WordCloud</div>
        <div style="font-size: 12px; color: #64748b;">Visualizing high-frequency terms extracted from visitor reviews</div>
    </div>
    """, unsafe_allow_html=True)
    wc_fig = generate_review_wordcloud(analysis_df)
    st.pyplot(wc_fig, use_container_width=True)

with col_freq:
    word_freq = get_top_review_words(analysis_df, top_n=12)
    fig_words = px.bar(
        word_freq,
        x='Frequency',
        y='Word',
        orientation='h',
        text='Frequency',
        color='Frequency',
        color_continuous_scale=px.colors.sequential.Teal,
        title="Top 12 Most Frequently Occurring Words"
    )
    fig_words.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_words.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_words), use_container_width=True)

# -------------------------------------------------------------
# ROW 2: SENTIMENT DISTRIBUTION & REVIEW COUNT BY DESTINATION
# -------------------------------------------------------------
col_senti, col_dest_rev = st.columns([1, 1.3])

with col_senti:
    senti_counts = analysis_df['Sentiment'].value_counts().reset_index()
    senti_counts.columns = ['Sentiment', 'Count']
    fig_s = px.pie(
        senti_counts,
        names='Sentiment',
        values='Count',
        hole=0.6,
        color='Sentiment',
        color_discrete_map={'Positive': '#10b981', 'Neutral': '#64748b', 'Negative': '#f43f5e'},
        title="VADER Sentiment Classification Split"
    )
    fig_s.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    st.plotly_chart(apply_pbi_theme(fig_s), use_container_width=True)

with col_dest_rev:
    dest_rev_counts = analysis_df['Place'].value_counts().head(10).reset_index()
    dest_rev_counts.columns = ['Place', 'Reviews_Count']
    fig_drc = px.bar(
        dest_rev_counts,
        x='Reviews_Count',
        y='Place',
        orientation='h',
        text='Reviews_Count',
        color='Reviews_Count',
        color_continuous_scale=px.colors.sequential.Blues,
        title="Top 10 Destinations by Volume of Reviews"
    )
    fig_drc.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_drc.update_traces(textposition='outside')
    st.plotly_chart(apply_pbi_theme(fig_drc), use_container_width=True)

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
    st.dataframe(display_reviews, use_container_width=True, height=280)
else:
    st.info("No reviews matched your search keyword.")

st.markdown("</div>", unsafe_allow_html=True)

