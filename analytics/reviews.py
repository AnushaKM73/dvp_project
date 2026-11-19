"""
Review & NLP Sentiment Analytics
"""

import json
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

CHART_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=12, color="#1e293b"),
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(248,250,252,0.6)",
    margin=dict(l=45, r=30, t=45, b=40),
    hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#ffffff", font_family="Inter"),
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0")
)


def apply_theme(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


def fig_to_dict(fig):
    return json.loads(fig.to_json())


STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
    "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
    'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
    'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't",
    'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
    "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won',
    "won't", 'wouldn', "wouldn't", 'place', 'visit', 'visited', 'places',
    'tour', 'trip', 'travel', 'one', 'get', 'also', 'really'
}


_VADER_CACHE = {}


def compute_vader_scores(reviews_series):
    """Compute VADER polarity scores and sentiment categories with caching."""
    if HAS_VADER:
        analyzer = SentimentIntensityAnalyzer()
        sentiments = []
        compound_scores = []
        for r in reviews_series:
            text = str(r) if pd.notna(r) else ""
            if text in _VADER_CACHE:
                sentiment, comp = _VADER_CACHE[text]
            else:
                scores = analyzer.polarity_scores(text)
                comp = round(scores['compound'], 3)
                if comp >= 0.05:
                    sentiment = "Positive"
                elif comp <= -0.05:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"
                _VADER_CACHE[text] = (sentiment, comp)
            compound_scores.append(comp)
            sentiments.append(sentiment)
        return sentiments, compound_scores
    else:
        # Rule-based fallback
        pos_words = {'great', 'good', 'excellent', 'amazing', 'wonderful', 'beautiful', 'awesome', 'best',
                     'loved', 'love', 'fantastic', 'nice', 'pleasant', 'superb', 'peaceful', 'stunning',
                     'breathtaking', 'memorable', 'clean', 'scenic', 'rich', 'must-visit', 'charming', 'worth'}
        neg_words = {'bad', 'poor', 'terrible', 'horrible', 'worst', 'dirty', 'crowded', 'expensive',
                     'disappointed', 'disappointing', 'rude', 'noisy', 'overrated', 'avoid', 'unpleasant'}
        sentiments = []
        compound_scores = []
        for r in reviews_series:
            text = str(r).lower() if pd.notna(r) else ""
            tokens = set(re.findall(r'\b[a-z]{3,}\b', text))
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


def get_review_analytics(df):
    """
    Calculate VADER sentiment breakdown, top review terms, and review charts.
    """
    if df.empty:
        return {
            "kpis": {
                "total_reviews": 0,
                "pos_cnt": 0,
                "pos_pct": 0.0,
                "neu_cnt": 0,
                "neu_pct": 0.0,
                "neg_cnt": 0,
                "neg_pct": 0.0,
                "avg_compound": 0.0,
                "has_vader": HAS_VADER
            },
            "charts": {}
        }

    analysis_df = df.copy()
    sentiments, comp_scores = compute_vader_scores(analysis_df['Review'])
    analysis_df['Sentiment'] = sentiments
    analysis_df['Polarity_Score'] = comp_scores

    total_reviews = len(analysis_df)
    pos_cnt = int((analysis_df['Sentiment'] == 'Positive').sum())
    neu_cnt = int((analysis_df['Sentiment'] == 'Neutral').sum())
    neg_cnt = int((analysis_df['Sentiment'] == 'Negative').sum())

    if total_reviews > 0:
        pos_pct = round(pos_cnt / total_reviews * 100, 1)
        neu_pct = round(neu_cnt / total_reviews * 100, 1)
        neg_pct = round(neg_cnt / total_reviews * 100, 1)
    else:
        pos_pct = neu_pct = neg_pct = 0.0

    avg_polarity = round(float(analysis_df['Polarity_Score'].mean()), 3) if not analysis_df.empty else 0.0

    # 1. Frequently Occurring Review Words (Replaces WordCloud with clean horizontal bar chart!)
    word_freq = {}
    for text in analysis_df['Review'].dropna():
        words = re.findall(r'\b[a-z]{3,}\b', str(text).lower())
        for w in words:
            if w not in STOPWORDS:
                word_freq[w] = word_freq.get(w, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:12]
    if sorted_words:
        wf_df = pd.DataFrame(sorted_words, columns=['Word', 'Frequency'])
        fig_words = px.bar(
            wf_df,
            x='Frequency',
            y='Word',
            orientation='h',
            text='Frequency',
            color='Frequency',
            color_continuous_scale=px.colors.sequential.Teal,
            title="Most Frequent Tourist Review Keywords & Descriptors"
        )
        fig_words.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        fig_words.update_traces(textposition='outside')
        apply_theme(fig_words)
    else:
        fig_words = go.Figure()

    # 2. Sentiment Doughnut
    sent_data = pd.DataFrame({
        'Sentiment': ['Positive', 'Neutral', 'Negative'],
        'Count': [pos_cnt, neu_cnt, neg_cnt]
    })
    fig_donut = px.pie(
        sent_data,
        names='Sentiment',
        values='Count',
        hole=0.6,
        color='Sentiment',
        color_discrete_map={
            'Positive': '#10b981',
            'Neutral': '#6366f1',
            'Negative': '#ef4444'
        },
        title="VADER Sentiment Classification Breakdown"
    )
    fig_donut.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    apply_theme(fig_donut)

    # 3. Top Destinations by Review Volume
    dest_reviews = analysis_df.groupby('Place').size().reset_index(name='Review_Count')
    dest_reviews = dest_reviews.sort_values(by='Review_Count', ascending=False).head(10)
    fig_dest_rev = px.bar(
        dest_reviews,
        x='Review_Count',
        y='Place',
        orientation='h',
        text='Review_Count',
        color='Review_Count',
        color_continuous_scale=px.colors.sequential.Bluyl,
        title="Top 10 Destinations by Tourist Review Volume"
    )
    fig_dest_rev.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    fig_dest_rev.update_traces(textposition='outside')
    apply_theme(fig_dest_rev)

    return {
        "kpis": {
            "total_reviews": total_reviews,
            "pos_cnt": pos_cnt,
            "pos_pct": pos_pct,
            "neu_cnt": neu_cnt,
            "neu_pct": neu_pct,
            "neg_cnt": neg_cnt,
            "neg_pct": neg_pct,
            "avg_compound": avg_polarity,
            "has_vader": HAS_VADER
        },
        "charts": {
            "word_frequency": fig_to_dict(fig_words),
            "sentiment_doughnut": fig_to_dict(fig_donut),
            "top_dest_reviews": fig_to_dict(fig_dest_rev)
        }
    }


def search_reviews(df, place="All Destinations", keyword=""):
    """Interactive Review Explorer filter and keyword search."""
    if df.empty:
        return []

    analysis_df = df.copy()
    sentiments, comp_scores = compute_vader_scores(analysis_df['Review'])
    analysis_df['Sentiment'] = sentiments
    analysis_df['Polarity_Score'] = comp_scores

    if place and place != "All Destinations" and place != "All":
        analysis_df = analysis_df[analysis_df['Place'] == place]

    if keyword and keyword.strip():
        kw = keyword.strip()
        analysis_df = analysis_df[analysis_df['Review'].str.contains(kw, case=False, na=False)]

    matched = analysis_df[['Visitor_ID', 'Place', 'State', 'Rating', 'Sentiment', 'Polarity_Score', 'Review']].copy()
    matched['Polarity_Score'] = matched['Polarity_Score'].round(3)
    return matched.head(100).to_dict(orient='records')

