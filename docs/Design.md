# UI/UX & Dashboard Design System

**Project Title:** Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark  
**Academic Context:** Big Data Analytics (BDA) Academic Mini-Project  
**Document Version:** 1.0.0  
**Status:** Approved Specification  

---

## 1. Design Philosophy & Academic Context

The user interface is an academic, vendor-oriented Big Data analytics dashboard built using **Streamlit** and **Plotly**. 

### 1.1 Core Principles
- **Data-First Clarity:** Visual elements exist to communicate analytical metrics without visual noise.
- **Academic Rigor & Professionalism:** The interface avoids consumer gamification, excessive glassmorphism, neon glow, and gratuitous animations. It mirrors institutional enterprise business intelligence platforms (e.g., Tableau, Databricks SQL, Apache Superset).
- **Zero-Latency Responsiveness:** Complex aggregations are computed upstream in PySpark. The dashboard renders pre-aggregated Parquet tables instantly, ensuring smooth interactions during faculty demonstrations.
- **Contextual Transparency:** Visualizations provide clear axis labels, data units (INR ₹, units, %), and tooltips explaining underlying metrics.

---

## 2. Visual Token System & Palette

The design utilizes a tailored modern dark-slate aesthetic that maximizes contrast and readability for dense data visualizations.

### 2.1 Color Palette
```text
Neutral Surfaces:
  Background (Dark):        #0F172A  (Deep Slate Navy)
  Surface / Card Base:      #1E293B  (Slate Card)
  Surface Elevated / Hover: #334155  (Slate Border / Hover)
  Text Primary:             #F8FAFC  (Crisp Off-White)
  Text Secondary / Muted:   #94A3B8  (Cool Gray)

Brand & Accents:
  Primary Accent:           #3B82F6  (Academic Blue)
  Secondary Accent:         #06B6D4  (Teal / Cyan)
  Tertiary Accent:          #8B5CF6  (Violet)

Semantic & Status Indicators:
  Success (Healthy Stock):  #10B981  (Emerald Green)
  Warning (Moderate Risk):  #F59E0B  (Amber Orange)
  Danger (Critical Stock):  #EF4444  (Crimson Red)
  Info (Notice / Baseline): #38BDF8  (Sky Blue)
```

### 2.2 Typography
- **Font Family:** System Sans-Serif stack prioritizing modern geometric sans:  
  `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Monospace (Code / IDs / Values):**  
  `"JetBrains Mono", "Fira Code", Consolas, Monaco, monospace`

| Level | Size | Weight | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Display / Title** | 28px (1.75rem) | 700 (Bold) | 1.2 | Main Dashboard Header |
| **Section Header (H2)** | 20px (1.25rem) | 600 (Semi-bold) | 1.3 | Tab & Panel Titles |
| **Card Header (H3)** | 16px (1.0rem) | 600 (Semi-bold) | 1.4 | KPI Titles & Chart Headers |
| **KPI Primary Value** | 32px (2.0rem) | 700 (Bold) | 1.1 | Numerical metric badges |
| **Body Text** | 14px (0.875rem)| 400 (Regular) | 1.5 | Explanatory text & descriptions |
| **Caption / Metadata** | 12px (0.75rem) | 400 (Regular) | 1.4 | Tooltips, axis ticks, timestamps |

---

## 3. Layout Structure & Navigation

The dashboard is structured into a collapsible control sidebar and a multi-tab main content viewport.

```
┌─────────────────┬─────────────────────────────────────────────────────────────┐
│  SIDEBAR        │  HEADER: Geo-Spatial E-Commerce Analytics (Spark Engine)   │
│  CONTROLS       ├─────────────────────────────────────────────────────────────┤
│                 │  [Tab 1: Overview] [Tab 2: Geo Trends] [Tab 3: Demand]     │
│  • Date Range   │  [Tab 4: Supply-Demand] [Tab 5: Discounts] [Tab 6: Actions] │
│  • Region/State ├─────────────────────────────────────────────────────────────┤
│  • City         │  [ KPI Card 1 ] [ KPI Card 2 ] [ KPI Card 3 ] [ KPI Card 4 ]│
│  • Category     ├──────────────────────────────┬──────────────────────────────┤
│  • Discount %   │  PRIMARY VISUALIZATION       │  SECONDARY METRICS / RANKING │
│  ─────────────  │  (e.g., Regional Bubble Map  │  (e.g., Top 10 Product Table │
│  [Reset Filter] │   or Elasticity Curve)       │   or Hourly Heatmap)         │
│                 │                              │                              │
└─────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### 3.1 Sidebar Filter Controls
The sidebar standardizes query criteria across all analytical tabs:
1. **Date Range Picker:** Single or multi-day window selection (defaults to full available period).
2. **Region / State Filter:** Multi-select dropdown (e.g., `All`, `Maharashtra`, `Karnataka`, `Delhi NCR`).
3. **City Filter:** Dynamically cascaded based on selected states (e.g., `Mumbai`, `Bengaluru`, `Pune`).
4. **Product Category Filter:** Multi-select dropdown (e.g., `Electronics`, `Apparel`, `Home Appliances`).
5. **Discount Range Slider:** Double-ended slider from `0%` to `70%`.
6. **Execution Telemetry Box:** Static summary badge showing dataset scale (e.g., `Processed Records: 5,000,000 | Spark Ingestion: Parquet`).

---

## 4. Component Design Specifications

### 4.1 KPI Metric Cards
KPI cards provide instant executive summaries at the top of each tab.

- **Container:** Slate card (`#1E293B`) with a subtle 1px border (`#334155`) and 8px border-radius.
- **Top Label:** Muted text (`#94A3B8`), 12px uppercase, letter-spaced.
- **Primary Metric:** Bold text (`#F8FAFC`), 28px–32px.
- **Delta / Context Indicator:** Semantic color badge indicating period-over-period or target status:
  - Green (`#10B981`): Positive conversion or balanced inventory.
  - Red (`#EF4444`): High shortage risk or margin compression.

### 4.2 Interactive Plotly Charts
All Plotly visualizations share a unified layout theme:
- **Plot Background:** Transparent or `#0F172A`.
- **Paper Background:** Transparent or `#1E293B`.
- **Grid Lines:** Subtle slate `#334155`, dashed, 0.5px.
- **Color Sequence:** `['#3B82F6', '#06B6D4', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']`.
- **Tooltips:** Dark slate background with high-contrast text and explicit currency/unit formatting.

### 4.3 Geo-Spatial Map Design (Plotly + OpenStreetMap)
- **Map Base:** OpenStreetMap or CartoDB Positron / Dark Matter tiles (free, non-commercial open layers; zero API keys required).
- **Coordinate Marker Style:** Circular scatter bubbles where:
  - **Size:** Mapped to Total Event Volume or Demand Score.
  - **Color:** Mapped to Conversion Rate or Stock-to-Demand Ratio.
- **Tooltip Hover Details:**
  - City & State Name
  - Total Events & Conversion Count
  - Calculated Demand Score
  - Current Available Inventory & Deficit Flag

### 4.4 Data Tables
- **Styling:** Compact row height (36px), alternating subtle zebra striping (`#1E293B` / `#172033`).
- **Header:** Sticky top header with bold font and clear column descriptors.
- **Alignment:** Text left-aligned; numerical values right-aligned.
- **Export Action:** Direct one-click "Download as CSV" button above each table.

---

## 5. Main Dashboard Tabs & Visual Hierarchies

### Tab 1: Executive Overview & KPIs
- **Top Row:** 4 KPI Cards:
  1. *Total Events Processed* (e.g., `5.2M`)
  2. *Gross Merchandise Value (GMV)* (e.g., `₹ 48.6 Cr`)
  3. *Total Unique Buyers* (e.g., `124,500`)
  4. *Overall Conversion Rate* (e.g., `3.42%`)
- **Main Section (Left):** Funnel Drop-off Bar Chart (Search $\rightarrow$ View $\rightarrow$ Cart $\rightarrow$ Purchase).
- **Side Section (Right):** Category Market Share Donut Chart.

### Tab 2: Regional & Geo-Spatial Trends
- **Primary View (Top):** Full-width interactive India/Global geographic bubble map displaying demand intensity by city.
- **Secondary View (Bottom Left):** Top 10 Trending Products by Selected City.
- **Secondary View (Bottom Right):** State-wise Gross Transaction Volume comparative bar chart.

### Tab 3: Demand Scoring & Temporal Patterns
- **Primary View (Top):** 24-Hour Circadian Demand Curve split across event types.
- **Secondary View (Bottom Left):** Day-of-Week Conversion Rate Bar Chart (Weekday vs. Weekend).
- **Secondary View (Bottom Right):** Category Demand Score Leaderboard.

### Tab 4: Supply-Demand Mismatch & Inventory Risk
- **Primary View (Top):** Supply vs. Demand Scatter Matrix:
  - X-Axis: Available Warehouse Stock
  - Y-Axis: Spark-Computed Demand Score
  - Quadrant Lines: Dividing Critical Shortage, Balanced, and Excess Inventory.
- **Secondary View (Bottom):** Filterable Critical Shortage Alert Table featuring one-click CSV export for warehouse procurement.

### Tab 5: Discount Optimization & Price Elasticity
- **Primary View (Top Left):** Sales Volume vs. Discount Bracket Bar Chart.
- **Primary View (Top Right):** Revenue Realization vs. Discount Bracket Line Chart.
- **Secondary View (Bottom):** Empirical Arc Elasticity Coefficient Distribution by Category (Highlighting Elastic vs. Inelastic categories).

### Tab 6: Actionable Business Recommendations
- **Format:** Structured card list and tabular view organized by priority:
  - **High Priority (Red Badge):** Urgent Stockout Prevention (Top-selling products with $SDR < 0.2$).
  - **Medium Priority (Amber Badge):** Clearance Liquidation (High inventory + elastic demand $\rightarrow$ 25% discount).
  - **Low Priority (Blue Badge):** Margin Recovery (Inelastic products currently over-discounted).
- **Card Contents:** Product Name, Category, Target Region, Quantitative Evidence, and Prescribed Action.

---

## 6. System States & UX Edge Cases

### 6.1 Empty States
- When a combination of sidebar filters yields 0 records, the dashboard displays an informative empty card:
  > **No Data Matches Selected Filters**  
  > *Adjust your date range or select additional regions to expand results.*

### 6.2 Loading States
- Streamlit's native `st.spinner("Computing regional aggregations from Parquet cache...")` is used during initial cold data loads.
- Data loading logic is wrapped in `@st.cache_data` to ensure all subsequent filter adjustments render in $< 200\text{ ms}$.

### 6.3 Error States
- If a processed Parquet file is missing (e.g., before Spark execution), an informative academic warning banner appears:
  > **Processed Dataset Not Found**  
  > *Please execute the PySpark analytics pipeline (`python scripts/run_pipeline.py`) to generate pre-aggregated Parquet artifacts.*
