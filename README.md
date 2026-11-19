# India Tourism Decision Lab

An interactive **Data Visualization with Python (DVP)** project for exploring a visitor sample, comparing destination patterns, and demonstrating how visual analytics can support a trip-planning decision.

## Project question

**How can interactive visualizations help us explore visitor patterns and compare destinations by experience, season, and estimated cost?**

The dashboard follows a simple path: **Explore the sample → Compare destinations → Plan an illustrative trip.**

## Important data boundary

The project contains two separate datasets. Do not combine their row counts or interpret them as the same kind of evidence.

### Visitor analytics sample

- File: `data/5dvp.csv`
- 1,000 rows, 20 destinations, 16 states, and 22 original columns
- Used for the dashboard KPIs, charts, ratings, costs, demographics, recommendations, and review demonstrations
- The repository does not record the dataset's original publisher or collection method. Treat results as patterns in this sample, not estimates for all Indian tourists.
- The sample has only eight distinct review phrases. VADER sentiment is included as a text-analysis demonstration and should not be presented as representative public opinion.

### Destination directory prototype

- File: `data/tourist_destinations_master.csv` (5,110 directory rows)
- Used only by the hierarchical map to demonstrate India → state → district → listing navigation
- The catalogue mixes a curated base list with generated district-template entries. Portal URLs are references, not proof that each listing was independently checked.
- Generated coordinates, ratings, costs, and stay lengths are illustrative. This file is not a verified official attractions register and must not be used to report visitor counts or factual destination scores.
- Details and limitations: [`data/district_coverage_report.md`](data/district_coverage_report.md)

## What the dashboard does

The root-level Flask app contains eight connected views:

1. **Executive Overview** — sample KPIs, an automated takeaway, and a dimension/metric explorer.
2. **Geographical Analysis** — visitor-sample destination markers and state/category comparisons.
3. **Tourist Demographics** — age, gender, travel-group, and age-by-group patterns.
4. **Tourism Performance** — satisfaction/popularity comparison, quality measures, and destination rankings.
5. **Financial Analysis** — budget matcher, configurable illustrative trip estimator, and cost patterns.
6. **Review Analytics** — keyword/review explorer and VADER text summaries, with the repeated-text limitation above.
7. **Recommender & Battle** — rule-based destination matching, an explainable score, pairwise comparison, and a 3D view.
8. **Interactive Map** — hierarchical browsing of the separate destination-directory prototype.

Global sidebar filters recalculate visitor-sample views. Clickable chart marks can add cross-filters; the selection bar shows and clears them. The destination-directory map remains a separate prototype view.

## How the recommendation score works

The destination matcher uses a transparent weighted rule, not machine learning or a probability:

| Criterion | Weight |
| --- | ---: |
| Theme fit | 30% |
| Budget fit | 25% |
| Average rating | 20% |
| Travel-group rating | 15% |
| Season evidence | 10% |

The dashboard displays the reasons and visitor-record counts behind recommendations. Scores describe compatibility with the selected preferences under this rule; they are not guaranteed outcomes.

## Technology

- **Backend:** Python, Flask, Pandas, NumPy
- **Charts:** Plotly
- **Maps:** Leaflet, GeoJSON, OpenStreetMap tiles
- **Text analysis:** VADER Sentiment
- **Frontend:** HTML, CSS, JavaScript

## Run the dashboard

Open PowerShell in the repository root (`D:\dvp_proj\dvp_project`) and run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Keep the terminal open while presenting. After code changes, restart the server and refresh with **Ctrl+F5**.

`run_dashboard.bat` launches the same root Flask app. For the current demo, use root-level `app.py`; older Streamlit files are retained from an earlier project iteration.

## Suggested demonstration story

1. Start with the overview and explain that the figures describe the 1,000-row sample.
2. Filter to a state or travel group, then click a chart mark to show cross-filtering.
3. Compare performance and cost for destinations represented in the visitor sample.
4. Open the recommender, explain the five score weights, and compare its top two suggestions.
5. Finish with the map as a separate GIS navigation prototype; state clearly that its catalogue and estimates are illustrative.

## Report and presentation guardrails

- Call dashboard values **sample results**; do not generalize them to all Indian tourists.
- Distinguish visitor records from destination-directory listings.
- Describe the matcher as a weighted rule-based recommender, not an AI prediction model.
- Describe the map catalogue as a prototype with portal references and approximate generated attributes.
- Cite the original publisher of `5dvp.csv` in the final report if your course brief or instructor supplies that source; it is not documented in this repository.
