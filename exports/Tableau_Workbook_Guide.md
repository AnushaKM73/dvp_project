# TABLEAU WORKBOOK CREATION & VISUALIZATION GUIDE
## Project: India Tourism Analytics & Business Intelligence Dashboard
### Course: Data Visualization with Python (DVP) Laboratory

This guide explains how to connect and build interactive dashboards in **Tableau Desktop / Tableau Public** using the verified datasets from this project.

---

## 1. Connecting Data in Tableau
1. Open **Tableau Desktop** or **Tableau Public**.
2. Click **Connect to Data** &rarr; **Text File** &rarr; Select `exports/tableau_tourism_dataset.csv` (or Microsoft Excel &rarr; `exports/India_Tourism_BI_Report.xlsx`).
3. Verify that geographical roles are assigned:
   * Field `Latitude` &rarr; Geographic Role: **Latitude**
   * Field `Longitude` &rarr; Geographic Role: **Longitude**
   * Field `State` &rarr; Geographic Role: **State/Province**

---

## 2. Tableau Calculated Fields to Create

### A. Recommendation Rate (%)
```tableau
SUM(IIF([Recommended] = "Yes", 1, 0)) / COUNT([Visitor ID])
```
*Format: Percentage with 1 decimal place.*

### B. Daily Travel Cost (INR / Day)
```tableau
[Estimated Cost INR] / [Stay Days]
```

### C. Cost Category Tier
```tableau
IF [Estimated Cost INR] < 2000 THEN "Budget (< ₹2,000)"
ELSEIF [Estimated Cost INR] <= 3500 THEN "Moderate (₹2,000 - ₹3,500)"
ELSE "Luxury (> ₹3,500)"
END
```

### D. Quality Index Score
```tableau
([Cleanliness Rating] + [Safety Rating] + [Accessibility Rating]) / 3
```

---

## 3. Worksheets to Build in Tableau

### Sheet 1: India Geospatial Symbol Map
* **Columns:** `Longitude` (Continuous)
* **Rows:** `Latitude` (Continuous)
* **Marks:** Circle
  * **Color:** `Category`
  * **Size:** `Visitors Count` (Sum)
  * **Detail:** `Place`, `State`
  * **Tooltip:** `Rating`, `Estimated Cost INR`, `Recommendation Rate`
* **Map Style:** Light / Streets

### Sheet 2: Category & Location Type Treemap
* **Marks:** Treemap
  * **Size:** Number of Records (`COUNT(Visitor ID)`)
  * **Color:** `Category`
  * **Label:** `Category`, `Location Type`, `COUNT(Visitor ID)`

### Sheet 3: Dual-Axis Monthly Demand vs Average Spend
* **Columns:** `Visit Month` (Sorted by calendar order)
* **Rows:** 
  * Axis 1: `COUNT(Visitor ID)` (Line Chart, Blue)
  * Axis 2: `AVG(Estimated Cost INR)` (Bar Chart, Light Gray)
* Click Axis 2 &rarr; **Dual Axis** &rarr; Synchronize Axis.

### Sheet 4: Performance Quadrant Scatter Plot
* **Columns:** `AVG(Popularity Score)`
* **Rows:** `AVG(Rating)`
* **Detail:** `Place`
* **Color:** `Category`
* Add Reference Lines:
  * Horizontal line at `4.4` (Average Rating)
  * Vertical line at `60.0` (Average Popularity)

---

## 4. Tableau Dashboard Layout & Interactive Actions
1. Create a new Dashboard (`1200 x 800` fixed or automatic size).
2. Arrange:
   * **Top:** 4 KPI Big Number Cards (Total Volume, States, Avg Rating, Avg Cost).
   * **Left:** Geospatial Symbol Map.
   * **Right:** Dual-Axis Monthly Chart & Treemap.
   * **Bottom:** Performance Quadrant Scatter Plot.
3. **Interactive Filter Action:**
   * Go to **Dashboard** &rarr; **Actions** &rarr; **Add Action** &rarr; **Filter**.
   * Source Sheet: **Map**.
   * Target Sheets: **All other sheets**.
   * Run Action on: **Select**.
   * *Selecting any destination or state on the India map instantly filters the entire Tableau dashboard!*

