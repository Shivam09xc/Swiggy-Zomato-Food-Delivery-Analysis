# 📊 Swiggy / Zomato Delivery Analytics: Power BI Design Manual
## 📌 Step-by-Step Dashboard Implementation & DAX Guide

This design guide outlines how to build a production-grade, highly engaging **4-Page Interactive Analytics Dashboard** inside **Power BI Desktop** using the cleaned and sentiment-enriched dataset `data/cleaned_data.csv`.

---

## 📥 Ingesting Data into Power BI
1. Launch **Power BI Desktop**.
2. Go to **Get Data** ➡️ **Text/CSV**.
3. Select `data/cleaned_data.csv` from the project repository.
4. Click **Load** to import the table.

---

## 🧠 Calculated DAX Measures (Data Modeling)
Create these calculated measures by right-clicking the `cleaned_data` table and selecting **New Measure**:

```dax
-- 1. Total Orders count
Total Orders = COUNT(cleaned_data[order_id])

-- 2. Total Sales Revenue (INR)
Total Revenue = SUM(cleaned_data[order_value])

-- 3. Average Order Value (AOV / Ticket Size)
AOV = DIVIDE([Total Revenue], [Total Orders], 0)

-- 4. Completed/Delivered Orders
Delivered Orders = CALCULATE([Total Orders], cleaned_data[order_status] = "Delivered")

-- 5. Cancelled Orders Volume
Cancelled Orders = CALCULATE([Total Orders], cleaned_data[order_status] = "Cancelled")

-- 6. Overall Cancellation Rate (%)
Cancellation Rate % = DIVIDE([Cancelled Orders], [Total Orders], 0) * 100

-- 7. Average Delivery Speed (Completed Orders Only)
Avg Delivery Time = CALCULATE(AVERAGE(cleaned_data[delivery_time]), cleaned_data[order_status] = "Delivered")

-- 8. Average Customer Rating Score (1-5 Stars)
Avg Rating Score = CALCULATE(AVERAGE(cleaned_data[rating]), cleaned_data[order_status] = "Delivered")
```

---

## 🎨 Global Styles & Dashboard Filters
* **Theme**: Apply the **"Slate"** or **"Dark Matter"** native Power BI theme to give it a premium dark-mode feel.
* **Global Slicer Panel (Place on the Left Margin on all 4 pages)**:
  * **Slicer 1**: `restaurant_name` (Set as a dropdown list or horizontal grid list).
  * **Slicer 2**: `delivery_area` (Set as a dropdown with search active).
  * **Slicer 3**: `category` (Set as a horizontal grid / tile slicer).

---

## 📑 Page-by-Page Visualizations Setup

### 1️⃣ Page 1: Executive Overview
*Goal: Provide a high-level command center showing revenue performance and category shares.*

1. **Executive KPI Cards (Top Banner)**:
   * **KPI Card 1**: `Total Orders` (Format as integer).
   * **KPI Card 2**: `Total Revenue` (Format as Currency: `₹0.00` in Lakhs).
   * **KPI Card 3**: `Avg Delivery Time` (Add decimal format `0.0` with standard label "mins").
   * **KPI Card 4**: `Avg Rating Score` (Format to 2 decimal places with star visual).
2. **Sales Revenue Trend (Line Chart)**:
   * **Axis (X)**: `order_date`
   * **Values (Y)**: `Total Revenue`
   * *Styling*: Set line color to Zomato Orange (`#dd6b20`), enable markers and data labels.
3. **Category Profitability (Donut Chart)**:
   * **Legend**: `category`
   * **Values**: `Total Revenue`
   * *Styling*: Use HSL tailored gradients.
4. **Restaurant Leaderboard (Table Grid)**:
   * **Columns**: `restaurant_name`, `Total Orders`, `Total Revenue`, `Avg Rating Score`, `Avg Delivery Time`.
   * *Formatting*: Apply conditional formatting data bars to the `Total Revenue` column.

---

### 2️⃣ Page 2: Delivery Performance
*Goal: Trace delivery delays, logistics latencies, and neighborhood density maps.*

1. **Zone Latency Ranks (Horizontal Clustered Bar Chart)**:
   * **Axis (Y)**: `delivery_area`
   * **Values (X)**: `Avg Delivery Time`
   * *Formatting*: Sort X-axis in **Ascending** order. Color bars by value gradient (faster = light green, slower = red/orange).
2. **Temporal Delay Trends (Line Chart)**:
   * **Axis (X)**: `order_hour`
   * **Values (Y)**: `AVERAGE(cleaned_data[delivery_delay])`
   * *Insight*: Easily tracks peak-hour traffic congestions during lunch (12-2 PM) and dinner (7-9 PM).
3. **Bengaluru Logistics Heatmap (Map Visual)**:
   * **Visual**: Bubble Map or ArcGIS Map.
   * **Latitude**: `latitude`
   * **Longitude**: `longitude`
   * **Bubble Size**: `Total Revenue`
   * **Bubble Color/Tooltips**: `Avg Delivery Time`
   * *Map Style*: Set background map theme to **Dark**.

---

### 3️⃣ Page 3: Customer Insights
*Goal: Isolate product rankings, customer retention metrics, and rating distributions.*

1. **Most Ordered Foods (Clustered Bar Chart)**:
   * **Axis (Y)**: `food_item`
   * **Values (X)**: `Total Orders`
   * *Formatting*: Apply top-N filtering to display only the **Top 10** food offerings.
2. **Customer Purchasing Loyalty (Donut Chart)**:
   * First, create a calculated column to group active buyers:
     ```dax
     Loyalty Bucket = 
     VAR CountOfOrders = CALCULATE(COUNT(cleaned_data[order_id]), ALLEXCEPT(cleaned_data, cleaned_data[customer_id]))
     RETURN 
     IF(CountOfOrders = 1, "1-Time Buyer", 
     IF(CountOfOrders = 2, "2-Time Buyer", 
     IF(CountOfOrders = 3, "3-Time Buyer", "4+ active VIPs")))
     ```
   * **Legend**: `Loyalty Bucket`
   * **Values**: `Total Orders`
3. **Ratings Distribution (Clustered Column Chart)**:
   * **Axis (X)**: `rating` (Convert to discrete text value / dimension)
   * **Values (Y)**: `Total Orders`

---

### 4️⃣ Page 4: Cancellation Dashboard
*Goal: Control and diagnostics of system failures, order dropouts, and cancelled refunds.*

1. **Area-Wise Cancellations (Clustered Bar Chart)**:
   * **Axis (Y)**: `delivery_area`
   * **Values (X)**: `Cancelled Orders`
   * *Color*: Set bar fill to Zomato Red (`#e53e3e`).
2. **Restaurant Outages (Clustered Bar Chart)**:
   * **Axis (Y)**: `restaurant_name`
   * **Values (X)**: `Cancelled Orders`
3. **Hourly Cancellation Trends (Line Chart)**:
   * **Axis (X)**: `order_hour`
   * **Values (Y)**: `Cancellation Rate %`
4. **Cancellation Root Cause Diagnostic Table**:
   * Create a filter on this table visual where `order_status` equals `Cancelled`.
   * **Columns**: `review` (which represents the cancellation reason generated by our simulation), `Cancelled Orders`.
   * *Formatting*: Sort descending by `Cancelled Orders` to display top operational reasons.
