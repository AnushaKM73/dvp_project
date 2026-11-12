"""
UI and Styling Components for Power BI-Style Streamlit Application
"""

import streamlit as st
import pandas as pd
from utils.data_cleaning import get_cached_cleaned_data, clean_tourism_data


CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0f172a;
    }

    /* Main Container Background */
    .stApp {
        background-color: #f8fafc;
    }

    /* Sidebar Styling (Dark Navy Power BI Aesthetic) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 13px;
    }

    /* Sidebar Dropdowns and Inputs */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
        border-radius: 8px;
    }

    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Power BI Metric / KPI Card */
    .pbi-kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }

    .pbi-kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }

    .pbi-kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #0284c7;
    }

    .pbi-kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: 6px;
    }

    .pbi-kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }

    .pbi-kpi-subtext {
        font-size: 11px;
        color: #10b981;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Power BI Chart Container */
    .pbi-chart-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }

    .pbi-chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 8px;
    }

    .pbi-chart-title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
    }

    .pbi-chart-subtitle {
        font-size: 12px;
        color: #64748b;
    }

    /* Page Header Banner */
    .pbi-header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 14px;
        padding: 24px 28px;
        color: #ffffff;
        margin-bottom: 24px;
        border: 1px solid #334155;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.1);
    }

    .pbi-badge {
        display: inline-block;
        background: rgba(2, 132, 199, 0.25);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Custom Tables */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }

    /* Streamlit tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 14px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        border-bottom: 3px solid #0284c7 !important;
        color: #0284c7 !important;
    }
</style>
"""


def apply_theme():
    """Inject custom Power BI stylesheet into the current Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_page_header(title, subtitle, badge="DVP LABORATORY PROJECT"):
    """Render a modern Power BI top banner."""
    st.markdown(f"""
    <div class="pbi-header-banner">
        <span class="pbi-badge">{badge}</span>
        <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff;">{title}</h1>
        <p style="margin: 6px 0 0 0; font-size: 13.5px; color: #94a3b8; font-weight: 400;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, subtext=None, border_color="#0284c7", icon="📊"):
    """Render an individual Power BI KPI Card."""
    subtext_html = f'<div class="pbi-kpi-subtext"><span>{subtext}</span></div>' if subtext else ''
    st.markdown(f"""
    <div class="pbi-kpi-card" style="border-left-color: {border_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="pbi-kpi-title">{title}</div>
            <span style="font-size: 16px;">{icon}</span>
        </div>
        <div class="pbi-kpi-value">{value}</div>
        {subtext_html}
    </div>
    """, unsafe_allow_html=True)


def init_session_data():
    """Initialize dataset and session state variables."""
    if 'raw_df' not in st.session_state:
        try:
            cleaned_df, audit = get_cached_cleaned_data(apply_record1_fix=True)
            st.session_state['cleaned_df'] = cleaned_df
            st.session_state['audit'] = audit
            st.session_state['record1_fixed'] = True
        except Exception as e:
            st.error(f"Error loading initial dataset: {e}")
            st.session_state['cleaned_df'] = pd.DataFrame()
            st.session_state['audit'] = {}
            st.session_state['record1_fixed'] = True

    if 'filters_applied' not in st.session_state:
        st.session_state['filters_applied'] = False
        st.session_state['filter_states'] = []
        st.session_state['filter_categories'] = []
        st.session_state['filter_location_types'] = []
        st.session_state['filter_seasons'] = []
        st.session_state['filter_months'] = []
        st.session_state['filter_age_groups'] = []
        st.session_state['filter_genders'] = []
        st.session_state['filter_travel_groups'] = []
        st.session_state['filter_recommended'] = []


def render_sidebar_filters():
    """
    Render global Power BI filter panel in the sidebar.
    Returns the filtered dataframe.
    """
    init_session_data()
    df = st.session_state.get('cleaned_df', pd.DataFrame())

    if df.empty:
        st.sidebar.warning("No dataset loaded.")
        return df

    st.sidebar.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1e293b; margin-bottom: 16px;">
        <div style="font-size: 11px; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 0.8px;">POWER BI FILTERS</div>
        <div style="font-size: 16px; font-weight: 700; color: #ffffff;">Global Slicers</div>
    </div>
    """, unsafe_allow_html=True)

    # First record correction toggle
    rec1_toggle = st.sidebar.toggle(
        "Python Record #1 Clean (Munnar)",
        value=st.session_state.get('record1_fixed', True),
        help="Applies Python laboratory fix for Visitor_ID V0001 (Munnar, Kerala)."
    )
    if rec1_toggle != st.session_state.get('record1_fixed', True):
        st.session_state['record1_fixed'] = rec1_toggle
        cleaned, audit = get_cached_cleaned_data(apply_record1_fix=rec1_toggle)
        st.session_state['cleaned_df'] = cleaned
        st.session_state['audit'] = audit
        st.rerun()

    # CSV File Uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload Custom CSV",
        type=["csv"],
        help="Upload an updated 5dvp.csv file to dynamically refresh all dashboards."
    )
    if uploaded_file is not None:
        try:
            user_raw = pd.read_csv(uploaded_file)
            cleaned, audit = clean_tourism_data(user_raw, apply_record1_fix=st.session_state['record1_fixed'])
            st.session_state['cleaned_df'] = cleaned
            st.session_state['audit'] = audit
            st.sidebar.success(f"Loaded {len(cleaned)} records!")
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV: {e}")

    # Available options for slicers
    all_states = sorted(df['State'].dropna().unique().tolist())
    all_categories = sorted(df['Category'].dropna().unique().tolist())
    all_loctypes = sorted(df['Location_Type'].dropna().unique().tolist())
    all_seasons = sorted(df['Season'].dropna().unique().tolist())
    all_months = sorted(df['Visit_Month'].dropna().unique().tolist())
    all_ages = sorted(df['Age_Group'].dropna().unique().tolist())
    all_genders = sorted(df['Gender'].dropna().unique().tolist())
    all_travel = sorted(df['Travel_Group'].dropna().unique().tolist())
    all_rec = sorted(df['Recommended'].dropna().unique().tolist())

    with st.sidebar.expander("🌍 Geography & Categories", expanded=False):
        sel_states = st.multiselect("Select State(s)", all_states, default=st.session_state.get('filter_states', []))
        sel_categories = st.multiselect("Select Category", all_categories, default=st.session_state.get('filter_categories', []))
        sel_loctypes = st.multiselect("Location Type", all_loctypes, default=st.session_state.get('filter_location_types', []))

    with st.sidebar.expander("📅 Season & Timing", expanded=False):
        sel_seasons = st.multiselect("Season", all_seasons, default=st.session_state.get('filter_seasons', []))
        sel_months = st.multiselect("Visit Month", all_months, default=st.session_state.get('filter_months', []))

    with st.sidebar.expander("👥 Visitor Demographics", expanded=False):
        sel_ages = st.multiselect("Age Group", all_ages, default=st.session_state.get('filter_age_groups', []))
        sel_genders = st.multiselect("Gender", all_genders, default=st.session_state.get('filter_genders', []))
        sel_travel = st.multiselect("Travel Group", all_travel, default=st.session_state.get('filter_travel_groups', []))
        sel_rec = st.multiselect("Recommended?", all_rec, default=st.session_state.get('filter_recommended', []))

    col_btn1, col_btn2 = st.sidebar.columns(2)
    apply_clicked = col_btn1.button("Apply", use_container_width=True, type="primary")
    reset_clicked = col_btn2.button("Reset", use_container_width=True)

    if reset_clicked:
        st.session_state['filter_states'] = []
        st.session_state['filter_categories'] = []
        st.session_state['filter_location_types'] = []
        st.session_state['filter_seasons'] = []
        st.session_state['filter_months'] = []
        st.session_state['filter_age_groups'] = []
        st.session_state['filter_genders'] = []
        st.session_state['filter_travel_groups'] = []
        st.session_state['filter_recommended'] = []
        st.session_state['filters_applied'] = False
        st.rerun()

    if apply_clicked:
        st.session_state['filter_states'] = sel_states
        st.session_state['filter_categories'] = sel_categories
        st.session_state['filter_location_types'] = sel_loctypes
        st.session_state['filter_seasons'] = sel_seasons
        st.session_state['filter_months'] = sel_months
        st.session_state['filter_age_groups'] = sel_ages
        st.session_state['filter_genders'] = sel_genders
        st.session_state['filter_travel_groups'] = sel_travel
        st.session_state['filter_recommended'] = sel_rec
        st.session_state['filters_applied'] = True

    # Filter evaluation
    filtered_df = df.copy()
    if st.session_state.get('filter_states'):
        filtered_df = filtered_df[filtered_df['State'].isin(st.session_state['filter_states'])]
    if st.session_state.get('filter_categories'):
        filtered_df = filtered_df[filtered_df['Category'].isin(st.session_state['filter_categories'])]
    if st.session_state.get('filter_location_types'):
        filtered_df = filtered_df[filtered_df['Location_Type'].isin(st.session_state['filter_location_types'])]
    if st.session_state.get('filter_seasons'):
        filtered_df = filtered_df[filtered_df['Season'].isin(st.session_state['filter_seasons'])]
    if st.session_state.get('filter_months'):
        filtered_df = filtered_df[filtered_df['Visit_Month'].isin(st.session_state['filter_months'])]
    if st.session_state.get('filter_age_groups'):
        filtered_df = filtered_df[filtered_df['Age_Group'].isin(st.session_state['filter_age_groups'])]
    if st.session_state.get('filter_genders'):
        filtered_df = filtered_df[filtered_df['Gender'].isin(st.session_state['filter_genders'])]
    if st.session_state.get('filter_travel_groups'):
        filtered_df = filtered_df[filtered_df['Travel_Group'].isin(st.session_state['filter_travel_groups'])]
    if st.session_state.get('filter_recommended'):
        filtered_df = filtered_df[filtered_df['Recommended'].isin(st.session_state['filter_recommended'])]

    # Sidebar Filter Status Badge
    active_filters_count = sum(bool(st.session_state.get(k)) for k in [
        'filter_states', 'filter_categories', 'filter_location_types',
        'filter_seasons', 'filter_months', 'filter_age_groups',
        'filter_genders', 'filter_travel_groups', 'filter_recommended'
    ])

    st.sidebar.markdown(f"""
    <div style="margin-top: 14px; padding: 10px 12px; background: #1e293b; border-radius: 8px; font-size: 12px; color: #94a3b8;">
        <div><b>Filter Status:</b> <span style="color: {'#38bdf8' if active_filters_count > 0 else '#64748b'};">{active_filters_count} active slicers</span></div>
        <div><b>Records:</b> <span style="color: #f8fafc; font-weight: 600;">{len(filtered_df):,}</span> of {len(df):,} ({len(filtered_df)/len(df)*100:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

    return filtered_df

