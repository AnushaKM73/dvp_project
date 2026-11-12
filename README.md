<<<<<<< HEAD
# INDIA TOURISM ANALYTICS AND BUSINESS INTELLIGENCE DASHBOARD
> **Tagline:** *Discover Destinations. Analyse Tourism. Visualize Insights.*  
> **Course:** Data Visualization with Python (DVP) Laboratory Project  

---

## 🌟 Executive Summary

**India Tourism Analytics and Business Intelligence Dashboard** is an academic Data Visualization with Python (DVP) laboratory project designed to provide business intelligence, geospatial mapping, demographic segmentation, financial expense modeling, and NLP review analytics for Indian tourism.

The project models approximately **1,000 tourist records** across **20 iconic Indian destinations** and **16 states/UTs**, implementing data preprocessing, statistical inference, interactive visual analytics, and **Power BI Desktop** data exports.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Core Language** | Python 3.10+ |
| **Data Processing & Analytics** | Pandas, NumPy |
| **Statistical Visualizations** | Matplotlib, Seaborn |
| **Interactive BI Visualizations** | Plotly, Plotly Express |
| **Geospatial Mapping** | Folium, Streamlit-Folium |
| **Text Mining & NLP** | WordCloud, VADER Sentiment Analysis |
| **Application Framework** | Streamlit (Power BI-inspired theme) |
| **Report Generation & BI** | OpenPyXL, Python CSV Engine |

---

## 📊 Dataset Schema (`5dvp.csv`)

The dataset comprises **1,000 rows** and **22 feature attributes**:

1. `Visitor_ID`: Unique traveler transaction identifier (`V0001` - `V1000`)
2. `State`: Indian State or Union Territory
3. `Place`: Renowned tourist landmark / destination (20 unique places)
4. `Address`: Administrative location details
5. `Category`: Tourism classification (`Nature`, `Historical`, `Cultural`, `Beach`, `Adventure`)
6. `Location_Type`: Geographic profile (`Hill Station`, `City`, `Heritage`, `Beach`, `Desert`, `Backwaters`)
7. `Best_Time_to_Visit`: Optimal climate window
8. `Visit_Month`: Calendar month of visit
9. `Season`: Season (`Winter`, `Summer`, `Monsoon`, `Spring`, `Autumn`)
10. `Age_Group`: Visitor age cohort (`18-25`, `26-35`, `36-50`, `51-65`, `65+`)
11. `Gender`: Gender representation (`Male`, `Female`, `Non-binary`, `Prefer not to say`)
12. `Travel_Group`: Travel party composition (`Solo`, `Couple`, `Family`, `Friends`, `Organized Group`)
13. `Review`: Visitor review text
14. `Rating`: Satisfaction score (1.0 to 5.0)
15. `Estimated_Cost_INR`: Trip cost in Indian Rupees (₹)
16. `Stay_Days`: Duration of trip in days
17. `Visitors_Count`: Estimated footfall volume
18. `Popularity_Score`: Normalized demand index (0 to 100)
19. `Cleanliness_Rating`: Sanitation score (1.0 to 5.0)
20. `Safety_Rating`: Tourist safety score (1.0 to 5.0)
21. `Accessibility_Rating`: Infrastructure accessibility score (1.0 to 5.0)
22. `Recommended`: Binary traveler advocacy recommendation (`Yes` / `No`)

---

## 🔬 Data Cleaning & Preprocessing Pipeline

Implemented in `utils/data_cleaning.py`:
1. **First Record Correction (Python Logic):** Repaired malformed initial record for `Visitor_ID: V0001` (Munnar, Kerala) with verified attributes. A toggle switch in the UI allows enabling or disabling this correction dynamically.
2. **Type Casting:** Numerical features converted from text strings into proper `float64` and `int64`.
3. **Missing Value Imputation:** Numerical missing values imputed using feature **median**; categorical missing values imputed using feature **mode**.
4. **Duplicate Handling:** Verified that no duplicate records skew the statistics.
5. **Geographical Coordinates:** Exact latitude and longitude coordinates attached for the 20 Indian destinations for mapping.

---

## 🖥️ Application Architecture & Dashboards

```text
dvp/
├── app.py                             # Main Landing Portal & Executive KPI Cards
├── data/
│   ├── 5dvp.csv                       # Raw source dataset
│   └── 5dvp_cleaned.csv               # Python cleaned dataset
├── pages/
│   ├── 1_Executive_Overview.py        # Power BI Executive KPI Dashboard
│   ├── 2_Geographical_Analysis.py     # Interactive Folium India GIS Map
│   ├── 3_Tourist_Demographics.py      # Age, gender & travel cohort heatmaps
│   ├── 4_Tourism_Performance.py       # Ratings, popularity & quality benchmarks
│   ├── 5_Financial_Analysis.py        # Expense modeling & budget simulator
│   ├── 6_Review_Analytics.py          # NLP WordClouds & VADER sentiment engine
│   ├── 7_Exploratory_Data_Analysis.py # Statistical EDA, IQR outliers & correlation
│   └── 8_Data_Explorer.py             # Data table, filters & Power BI exports
├── utils/
│   ├── data_cleaning.py               # Preprocessing & imputation routines
│   ├── data_analysis.py               # Statistical aggregations & metrics
│   ├── visualizations.py              # Plotly, Matplotlib, Seaborn, Folium charts
│   ├── insights.py                    # Dynamic algorithmic business insights
│   ├── report_generator.py            # OpenPyXL multi-tab Excel & CSV generator
│   └── ui_components.py               # Custom CSS & Power BI sidebar slicers
├── exports/                           # Power BI ready dimension tables (.csv)
├── requirements.txt                   # Project dependencies
└── README.md                          # Laboratory documentation
```

---

## 🚀 How to Run the Application

### 1. Ensure Dependencies are Installed
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit Application
```bash
streamlit run app.py
```

The application will launch automatically in your web browser at:
`http://localhost:8501`

---

## 💼 Power BI Desktop Integration

The application generates Star-Schema compatible tables in `exports/` and a consolidated multi-tab Excel report: `exports/India_Tourism_BI_Report.xlsx`.

### Importing into Power BI Desktop:
1. Open **Power BI Desktop**.
2. Click **Get Data** &rarr; **Excel Workbook** &rarr; Select `India_Tourism_BI_Report.xlsx`.
3. Select sheets:
   - `Cleaned_Data` (Fact Table)
   - `Destination_Master` (Dimension Table)
   - `State_Analysis` (Dimension Table)
   - `Category_Insights` (Dimension Table)
   - `Monthly_Trends` (Dimension Table)
4. Model Relationships:
   - `Cleaned_Data[Place]` &rarr; `Destination_Master[Place]` (Many-to-One)
   - `Cleaned_Data[State]` &rarr; `State_Analysis[State]` (Many-to-One)
   - `Cleaned_Data[Category]` &rarr; `Category_Insights[Category]` (Many-to-One)

---

## 🎓 Laboratory Presentation Highlights for Faculty

* **Dynamic Python Calculations:** Zero hardcoded dashboard values; all charts, KPIs, and insights calculate dynamically based on active filters.
* **Global Filter Panel:** Interactive sidebar slicers (State, Category, Season, Age Group, Gender, Travel Group) that synchronously update all charts and tables.
* **Interactive India GIS Mapping:** Accurate geographical coordinates for all 20 Indian landmarks rendered with category color badges and interactive popups.
* **NLP & Text Mining:** Stopword-filtered WordCloud and real VADER sentiment analysis on tourist reviews.
* **Rigorous Statistical EDA:** Parametric distributions, skewness analysis, IQR outlier fences, and correlation heatmaps with Seaborn.

=======
# dvp_project
>>>>>>> 36cbd289d3a72f69c04fe4dcdd073a6969b53023
