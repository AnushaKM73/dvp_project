# DVP Demo and Viva Guide

## One-sentence project explanation

**India Tourism Decision Lab is an interactive Flask dashboard that explores patterns in a 1,000-row tourism visitor sample and demonstrates how filters, linked charts, and a transparent preference score can support destination comparison.**

## Three-minute live demo

1. **Executive Overview (30 sec):** State that the KPIs summarize the supplied visitor sample, then point out the sample size and the main takeaway. Avoid calling it a survey of all Indian tourists.
2. **Show interaction (30 sec):** Select a state or travel group in the global filters. Explain that the charts recalculate for the selected subset. Click a chart mark to add a cross-filter, then clear it with the selection bar.
3. **Explain one insight (30 sec):** Open Tourism Performance or Geographical Analysis. Identify the chart type, its axes, and what one visible comparison means. Say “in this sample” when describing the result.
4. **Show the decision tool (45 sec):** Open Recommender & Battle. Change preferences, inspect the suggested destinations, and explain that the score is a weighted rule: theme 30%, budget 25%, rating 20%, travel-group rating 15%, season 10%. Compare two destinations and point out the reasons; this is not machine learning.
5. **Close with the map (30 sec):** Show India → state → district navigation. Explain that the map uses a separate directory prototype; generated entries and attributes are illustrative and do not represent observed visitor counts.
6. **State the limitation (15 sec):** The visitor file's original publisher and collection method are not documented in this repository, and review text contains only eight distinct phrases. Results should be treated as sample exploration, not population-level conclusions.

## Report / presentation structure

1. **Problem and objective:** Why an interactive tourism exploration tool is useful.
2. **Data and scope:** Describe `data/5dvp.csv` (1,000 rows) and the separate destination-directory prototype. Include provenance limitations.
3. **Preparation:** Explain the cleaning pipeline, correction of the first record, and destination coordinate lookup used for mapping. Mention the treatment of missing or inconsistent values only after checking the code and dataset.
4. **Visualization design:** Group the dashboard into visitor overview, place/geography, visitor segments, performance/cost, reviews, and decision support. Explain a few charts by chart type, variables, and interaction.
5. **Recommendation method:** Present the five weights and explain that this is a transparent heuristic score.
6. **Findings:** Choose two or three concrete results from the dashboard and qualify each as a pattern in this sample.
7. **Limitations and future work:** Dataset provenance, repeated reviews, illustrative directory fields, and how verified row-level sources could improve the map.
8. **Conclusion:** The value is the linked exploration and explainable comparison workflow, not a claim that the dashboard predicts national tourism behavior.

## Likely viva questions

**What is the project doing?**  
It lets a user explore a tourism visitor sample through interactive visualizations and compare destinations using an explainable preference score.

**Why use interactive charts?**  
Filters and chart selections let the viewer investigate subsets and relationships instead of looking at fixed summaries only.

**What does a bar chart show?**  
It compares values across categories; the bar length encodes the measure. Read the category axis and value axis before stating an insight.

**What is cross-filtering?**  
Selecting a category in one chart adds a filter that updates other dashboard views. Clearing the selection returns to the broader sample.

**Is the recommender AI or machine learning?**  
No. It is a rule-based weighted score with visible criteria. Its suggestions depend on the chosen weights and available sample fields.

**What does a rating represent?**  
It is the rating value recorded in the visitor sample and summarized for the current filter selection. It is not independently verified ground truth.

**Why does the map use a different dataset?**  
The visitor sample covers a small set of destinations. A separate directory supports hierarchical map navigation, but some entries and attributes are illustrative and must not be mixed with visitor counts.

**What is the main limitation?**  
The visitor dataset's original source and collection method are undocumented in this repository, so the results cannot be generalized to all tourists.

**What would you improve next?**  
Obtain a documented, representative visitor dataset and replace illustrative map entries with individually verified attractions, coordinates, and direct source links.

## Before presenting

- Start the Flask app from the repository root with `python app.py` and open `http://127.0.0.1:5000`.
- Check that the dashboard loads and that one global filter and one chart click update the other views.
- Keep the terminal open. If code changes were made while it was running, restart the app and refresh the page.
- Prepare two actual observations from the current dashboard and note which filters were active when you saw them.
