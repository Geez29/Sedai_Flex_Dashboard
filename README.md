
# Sedai Cost Optimization Dashboard (Streamlit)

One-page **Sedai** dashboard in **Python + Streamlit** with McKinsey-style colors. Includes filters (Month, Year, FY, Sprint), a top-right **Flex** logo, and a mix of funnel, bar and pie charts with $-value labels. Tables summarize recommendations and savings per Sprint.

## Features
- **Filters**: Month, Year, FY (Apr 1 → Mar 31 *end-year* label), Sprint
- **KPIs**: Total Recommendations, Total Savings ($), Total Savings (%) [= Total Savings $ / Total Current $], Avg Savings / Recommendation ($)
- **Charts** (all with $ labels):
  - **Savings Pipeline (Funnel)** – Initiated → Delayed → Unachieveable → Achieved
  - **Savings by Inference Type (Bar)**
  - **Recommendations by Sprint & Savings ($)** – dual-axis bar + line
  - **Savings Mix (Pie)** – Achieved / Unachieveable / Delayed / Initiated
- **Table**: Sprint summary with $ and **counts** per category (Initiated, Achieved, Unachievable, Delayed)
- **Logo**: Flex logo (placeholder) at top-right (replace with your asset in `assets/flex_logo.png`).

## Data
The app expects an **Execution report**-style XLSX file (like `sedai_execution_report_sample_v4.xlsx`). Required columns (case-insensitive):

```
Sprint, Start Date, End Date, Inference Type, Region, Cloud Provider,
Current Monthly Cost ($), Est. Monthly Cost ($), Cost Savings in $, Cost Savings in %,
Achieved Savings, Unachieveable Savings, Delayed Savings, Initiated
```

> **Fiscal Year**: Apr 1 to Mar 31. FY label uses the *end year* (e.g., Apr 2024–Mar 2025 ⇒ **FY2025**). Quarters: **Q1=Apr–Jun**, **Q2=Jul–Sep**, **Q3=Oct–Dec**, **Q4=Jan–Mar**.

## Getting Started

### 1) Clone or download
```bash
# create and activate venv (optional)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install requirements
pip install -r requirements.txt
```

### 2) Place your data & logo
- Copy your dataset (e.g., `sedai_execution_report_sample_v4.xlsx`) into the same folder.
- Replace `assets/flex_logo.png` with your official logo if desired.

### 3) Run
```bash
streamlit run app.py
```

Open the link shown in terminal (usually http://localhost:8501).

## Customization
- **Color palette**: update `COLORS` and `CATEGORY_COLORS` in `app.py`.
- **Default file**: change the `default_path` parameter in `load_data()`.
- **New visuals**: add more Plotly charts—`flt` holds the filtered DataFrame.

## Notes
- Total Savings (%) on KPIs and table uses **weighted** definition: `sum(Cost Savings $) / sum(Current $)`.
- If date fields are missing, the app falls back to today’s date for filter derivation (Month/Year/FY).

---
© Flex – Internal tooling demo
