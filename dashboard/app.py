import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
# 🌟 Page Configuration & Theme Setup
# ----------------------------------------------------
st.set_page_config(
    page_title="Swiggy / Zomato Delivery Insights",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via HTML injection
st.markdown("""
<style>
    /* Dark Mode Glassmorphic styling */
    .stApp {
        background-color: #0c0f16;
        color: #e2e8f0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #141a24 !important;
        border-right: 1px solid #2d3748;
    }
    
    /* Elegant Title Banner */
    .title-banner {
        background: linear-gradient(135deg, #e53e3e 0%, #dd6b20 50%, #319795 100%);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .title-banner h1 {
        color: white !important;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        margin-bottom: 5px !important;
    }
    .title-banner p {
        color: #f7fafc !important;
        font-size: 1.1rem;
        font-weight: 300;
        margin: 0 !important;
    }

    /* KPI Metrics Cards styling */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: linear-gradient(145deg, #182232, #111823);
        border: 1px solid #23354d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        flex: 1;
        transition: transform 0.3s ease, border-color 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #e53e3e;
    }
    .kpi-title {
        color: #a0aec0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .kpi-sub {
        color: #48bb78;
        font-size: 0.75rem;
        margin-top: 4px;
    }
    .kpi-sub-neg {
        color: #e53e3e;
        font-size: 0.75rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 📦 Data Ingestion
# ----------------------------------------------------
@st.cache_data
def load_data():
    file_path = "data/cleaned_data.csv"
    if not os.path.exists(file_path):
        file_path = "../data/cleaned_data.csv"
        if not os.path.exists(file_path):
            st.error("❌ Data file 'cleaned_data.csv' not found. Please run the pipeline script first!")
            return pd.DataFrame()
            
    df = pd.read_csv(file_path)
    # Add mockup coordinates for Bengaluru delivery areas
    coordinates = {
        "Indiranagar": (12.9719, 77.6412),
        "Koramangala": (12.9279, 77.6271),
        "HSR Layout": (12.9101, 77.6450),
        "Whitefield": (12.9698, 77.7499),
        "Jayanagar": (12.9292, 77.5824),
        "Marathahalli": (12.9569, 77.7011),
        "BTM Layout": (12.9166, 77.6101),
        "Malleshwaram": (12.9984, 77.5703)
    }
    df['latitude'] = df['delivery_area'].map(lambda x: coordinates.get(x, (12.9716, 77.5946))[0] + (0.004 * (hash(x) % 5 - 2)))
    df['longitude'] = df['delivery_area'].map(lambda x: coordinates.get(x, (12.9716, 77.5946))[1] + (0.004 * (hash(x) % 7 - 3)))
    return df

df_full = load_data()

if df_full.empty:
    st.stop()

# ----------------------------------------------------
# 🎛️ Sidebar Configuration & Filters
# ----------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/bd/Firebase_Logo.png", width=50, caption="Operational Dashboard Hub")

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page:", [
    "1️⃣ Executive Overview",
    "2️⃣ Delivery Performance",
    "3️⃣ Customer Insights",
    "4️⃣ Cancellation Dashboard",
    "🚀 Advanced AI & Real-Time Engine"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Panel")

# Multi-select filters
all_restaurants = sorted(df_full['restaurant_name'].unique())
selected_restaurants = st.sidebar.multiselect("Restaurants", all_restaurants, default=[])

all_areas = sorted(df_full['delivery_area'].unique())
selected_areas = st.sidebar.multiselect("Delivery Areas", all_areas, default=[])

all_categories = sorted(df_full['category'].unique())
selected_categories = st.sidebar.multiselect("Food Categories", all_categories, default=[])

# Apply Filters to a local copy
df = df_full.copy()

if selected_restaurants:
    df = df[df['restaurant_name'].isin(selected_restaurants)]
if selected_areas:
    df = df[df['delivery_area'].isin(selected_areas)]
if selected_categories:
    df = df[df['category'].isin(selected_categories)]

# Common Calculated Variables
total_orders = len(df)
delivered_orders = len(df[df['order_status'] == 'Delivered'])
cancelled_orders = len(df[df['order_status'] == 'Cancelled'])

total_revenue = df['order_value'].sum()
avg_delivery_time = df[df['order_status'] == 'Delivered']['delivery_time'].mean()
avg_rating = df[df['order_status'] == 'Delivered']['rating'].mean()
cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0.0

# ----------------------------------------------------
# 🏆 Shared KPI Cards Render Function
# ----------------------------------------------------
def render_kpis():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Total Orders</div>
            <div class='kpi-value'>{total_orders:,}</div>
            <div class='kpi-sub'>Completed: {delivered_orders:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Total Revenue</div>
            <div class='kpi-value'>₹{total_revenue/100000:.2f}L</div>
            <div class='kpi-sub'>AOV: ₹{df['order_value'].mean():.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Avg Delivery Time</div>
            <div class='kpi-value'>{avg_delivery_time:.1f}m</div>
            <div class='kpi-sub'>Target Goal: 30m</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Avg Rating</div>
            <div class='kpi-value'>★ {avg_rating:.2f}</div>
            <div class='kpi-sub'>Sentiment Polarity: {df[df['order_status'] == 'Delivered']['sentiment_polarity'].mean():.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ========================================================
# 1️⃣ PAGE 1: EXECUTIVE OVERVIEW
# ========================================================
if page == "1️⃣ Executive Overview":
    st.markdown("""
    <div class='title-banner'>
        <h1>1️⃣ Executive Operations Overview</h1>
        <p>Strategic High-Level KPIs, Sales Revenue Performance, and Category Contributions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render KPI Cards
    render_kpis()
    
    row1, row2 = st.columns(2)
    with row1:
        # Sales revenue trend over the 30-day period
        df['order_date'] = pd.to_datetime(df['order_date'])
        revenue_trend = df.groupby('order_date')['order_value'].sum().reset_index()
        
        fig_rev = px.line(
            revenue_trend,
            x='order_date',
            y='order_value',
            markers=True,
            title="Daily Sales Revenue Trend (INR)",
            labels={'order_date': 'Transaction Date', 'order_value': 'Sales (INR)'},
            color_discrete_sequence=['#e53e3e']
        )
        fig_rev.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#23354d')
        )
        st.plotly_chart(fig_rev, width='stretch')
        
    with row2:
        # Donut Chart of Sales Category contributions
        cat_share = df.groupby('category')['order_value'].sum().reset_index()
        fig_cat = px.pie(
            cat_share,
            values='order_value',
            names='category',
            title="Category Share of Revenue Contribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_cat.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cat, width='stretch')

    # Top Restaurants Performance Table
    st.markdown("### 🏆 Restaurant Performance Leaderboard")
    rest_perf = df.groupby('restaurant_name').agg(
        orders=('order_id', 'count'),
        revenue=('order_value', 'sum'),
        rating=('rating', 'mean'),
        time=('delivery_time', 'mean')
    ).reset_index().sort_values(by='revenue', ascending=False)
    
    st.dataframe(
        rest_perf.rename(columns={
            'restaurant_name': 'Restaurant Name',
            'orders': 'Orders Count',
            'revenue': 'Total Sales',
            'rating': 'Avg Star Rating',
            'time': 'Avg Delivery Speed (Mins)'
        }),
        column_config={
            "Total Sales": st.column_config.NumberColumn(format="₹%d"),
            "Avg Star Rating": st.column_config.NumberColumn(format="★ %.2f"),
            "Avg Delivery Speed (Mins)": st.column_config.NumberColumn(format="%.1f min")
        },
        hide_index=True,
        width='stretch'
    )


# ========================================================
# 2️⃣ PAGE 2: DELIVERY PERFORMANCE
# ========================================================
elif page == "2️⃣ Delivery Performance":
    st.markdown("""
    <div class='title-banner'>
        <h1>2️⃣ Logistics & Delivery Performance</h1>
        <p>Geospatial Hotspots, Neighborhood Latencies, and Hourly Delay Dynamics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render KPIs
    render_kpis()
    
    row1, row2 = st.columns(2)
    with row1:
        # Fastest delivery areas (Horizontal Bar Chart)
        avg_time_area = df[df['order_status'] == 'Delivered'].groupby('delivery_area')['delivery_time'].mean().reset_index().sort_values(by='delivery_time')
        fig_area = px.bar(
            avg_time_area,
            y='delivery_area',
            x='delivery_time',
            orientation='h',
            title="Fastest Delivery Neighborhood Zones (Sorted by Speed)",
            labels={'delivery_area': 'Zone', 'delivery_time': 'Avg Time (Mins)'},
            color='delivery_time',
            color_continuous_scale=px.colors.sequential.Sunsetdark
        )
        fig_area.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='#23354d'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_area, width='stretch')
        
    with row2:
        # Delay trends by hour (Minutes delayed beyond 30 mins)
        delivered_only = df[df['order_status'] == 'Delivered'].copy()
        avg_delay_hour = delivered_only.groupby('order_hour')['delivery_delay'].mean().reset_index()
        
        fig_delay = px.line(
            avg_delay_hour,
            x='order_hour',
            y='delivery_delay',
            markers=True,
            title="Average Latency Delay Beyond 30-Minute Target by Hour",
            labels={'order_hour': 'Hour of Day (24h)', 'delivery_delay': 'Avg Delay (Mins)'},
            color_discrete_sequence=['#dd6b20']
        )
        fig_delay.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickmode='linear', tick0=0, dtick=2),
            yaxis=dict(showgrid=True, gridcolor='#23354d')
        )
        st.plotly_chart(fig_delay, width='stretch')

    # Heatmap / Operational map of busy Bengaluru areas
    st.markdown("### 📍 Bengaluru Delivery Geo-Hotspots Heatmap")
    map_df = df[df['order_status'] == 'Delivered'].copy()
    
    fig_map = px.scatter_map(
        map_df,
        lat="latitude",
        lon="longitude",
        size="order_value",
        color="delivery_time",
        color_continuous_scale=px.colors.sequential.Sunsetdark,
        size_max=12,
        zoom=11.2,
        title="Operational Speed Heatmap (Bubble Size = Revenue, Color = Delivery Time)",
        hover_name="restaurant_name",
        hover_data=["delivery_area", "food_item", "delivery_time", "rating"]
    )
    fig_map.update_layout(
        map_style="carto-darkmatter",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=35, b=0),
        coloraxis_colorbar=dict(title="Time (m)")
    )
    st.plotly_chart(fig_map, width='stretch')


# ========================================================
# 3️⃣ PAGE 3: CUSTOMER INSIGHTS
# ========================================================
elif page == "3️⃣ Customer Insights":
    st.markdown("""
    <div class='title-banner'>
        <h1>3️⃣ Customer Quality & Order Insights</h1>
        <p>Top Food Offerings, Star Ratings Distributions, and Repeat Customer Loyalty Metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_kpis()
    
    row1, row2 = st.columns(2)
    with row1:
        # Top foods (Bar Chart)
        top_foods = df.groupby('food_item').size().reset_index(name='order_count').sort_values(by='order_count', ascending=False).head(10)
        fig_food = px.bar(
            top_foods,
            x='order_count',
            y='food_item',
            orientation='h',
            title="Top 10 Most Ordered Food Offerings (Volume)",
            labels={'food_item': 'Food Item', 'order_count': 'Total Orders'},
            color='order_count',
            color_continuous_scale=px.colors.sequential.Sunsetdark
        )
        fig_food.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='#23354d'),
            yaxis=dict(showgrid=False, categoryorder='total ascending')
        )
        st.plotly_chart(fig_food, width='stretch')
        
    with row2:
        # Repeat customers (loyalty)
        # We calculate the count of orders placed per customer
        cust_orders = df.groupby('customer_id').size().reset_index(name='orders_count')
        # Segment into 1 order, 2 orders, 3 orders, 4+ orders
        cust_orders['loyalty_bucket'] = pd.cut(
            cust_orders['orders_count'],
            bins=[0, 1, 2, 3, 100],
            labels=['1-Time Buyers', '2-Time Buyers', '3-Time Buyers', '4+ Active VIPs']
        )
        repeat_dist = cust_orders['loyalty_bucket'].value_counts().reset_index()
        repeat_dist.columns = ['Loyalty Segment', 'Customer Count']
        
        fig_loy = px.pie(
            repeat_dist,
            values='Customer Count',
            names='Loyalty Segment',
            title="Customer Purchasing Loyalty & Frequency Breakdown",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_loy.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_loy, width='stretch')

    # Ratings distribution
    st.markdown("### ⭐ Customer Star Ratings Distribution")
    delivered_only = df[df['order_status'] == 'Delivered'].copy()
    ratings_dist = delivered_only['rating'].value_counts().reset_index()
    ratings_dist.columns = ['Rating', 'Orders']
    ratings_dist = ratings_dist.sort_values(by='Rating')
    
    fig_rate = px.bar(
        ratings_dist,
        x='Rating',
        y='Orders',
        title="Star Ratings Distribution Profile (Delivered Orders)",
        labels={'Rating': 'Star Rating (1-5)', 'Orders': 'Volume (Orders)'},
        color='Rating',
        color_continuous_scale=px.colors.sequential.solar
    )
    fig_rate.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False, tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#23354d')
    )
    st.plotly_chart(fig_rate, width='stretch')


# ========================================================
# 4️⃣ PAGE 4: CANCELLATION DASHBOARD
# ========================================================
elif page == "4️⃣ Cancellation Dashboard":
    st.markdown("""
    <div class='title-banner'>
        <h1>4️⃣ Cancellations Operations Control</h1>
        <p>Geographic Failures, Restaurant Outages, and Root Cause Diagnostics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs custom render showing cancellation metrics
    render_kpis()
    
    row1, row2 = st.columns(2)
    with row1:
        # Area-wise cancellations (Bar Chart)
        cancelled_only = df[df['order_status'] == 'Cancelled']
        area_cancels = cancelled_only.groupby('delivery_area').size().reset_index(name='cancels').sort_values(by='cancels', ascending=False)
        
        fig_area_c = px.bar(
            area_cancels,
            x='cancels',
            y='delivery_area',
            orientation='h',
            title="Area-Wise Order Cancellations Volume",
            labels={'delivery_area': 'Zone', 'cancels': 'Cancelled Orders'},
            color='cancels',
            color_continuous_scale=px.colors.sequential.Reds
        )
        fig_area_c.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='#23354d'),
            yaxis=dict(showgrid=False, categoryorder='total ascending')
        )
        st.plotly_chart(fig_area_c, width='stretch')
        
    with row2:
        # Restaurant-wise cancellations (Bar Chart)
        rest_cancels = cancelled_only.groupby('restaurant_name').size().reset_index(name='cancels').sort_values(by='cancels', ascending=False)
        fig_rest_c = px.bar(
            rest_cancels,
            x='cancels',
            y='restaurant_name',
            orientation='h',
            title="Restaurant Brand Cancellations Volume",
            labels={'restaurant_name': 'Restaurant Name', 'cancels': 'Cancelled Orders'},
            color='cancels',
            color_continuous_scale=px.colors.sequential.Reds
        )
        fig_rest_c.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='#23354d'),
            yaxis=dict(showgrid=False, categoryorder='total ascending')
        )
        st.plotly_chart(fig_rest_c, width='stretch')

    # Cancellation trends by hour
    st.markdown("### 📈 Hourly Cancellation Rate Trends")
    hourly_cancels = df.groupby('order_hour').agg(
        total=('order_id', 'count'),
        cancels=('order_status', lambda x: (x == 'Cancelled').sum())
    ).reset_index()
    hourly_cancels['cancel_rate'] = (hourly_cancels['cancels'] / hourly_cancels['total'] * 100).round(2)
    
    fig_trend_c = px.line(
        hourly_cancels,
        x='order_hour',
        y='cancel_rate',
        markers=True,
        title="Hourly Order Cancellation Rate (%) Pattern",
        labels={'order_hour': 'Hour of Day (24h)', 'cancel_rate': 'Cancellation Rate %'},
        color_discrete_sequence=['#e53e3e']
    )
    fig_trend_c.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickmode='linear', tick0=0, dtick=2),
        yaxis=dict(showgrid=True, gridcolor='#23354d')
    )
    st.plotly_chart(fig_trend_c, width='stretch')

    # Text root-cause breakdown
    st.markdown("##### 🔍 Systemic Root Causes of Cancellations")
    if cancelled_orders > 0:
        cancellation_causes = cancelled_only.groupby('review').size().reset_index(name='Occurrences').sort_values(by='Occurrences', ascending=False)
        cancellation_causes['Share Percentage'] = (cancellation_causes['Occurrences'] / cancelled_orders * 100).round(1).astype(str) + '%'
        
        st.dataframe(
            cancellation_causes.rename(columns={'review': 'Cancellation Root Cause Reason'}),
            column_config={
                "Cancellation Root Cause Reason": st.column_config.TextColumn("Cancellation Reason Category", width="large"),
                "Occurrences": st.column_config.NumberColumn("Cancelled Orders"),
                "Share Percentage": st.column_config.TextColumn("Systemic Share")
            },
            hide_index=True,
            width='stretch'
        )
    else:
        st.info("Zero cancellations are present in the current sliced dataset.")

# ========================================================
# 🚀 PAGE 5: ADVANCED AI & REAL-TIME ENGINE
# ========================================================
elif page == "🚀 Advanced AI & Real-Time Engine":
    st.markdown("""
    <div class='title-banner'>
        <h1>🚀 Advanced AI & Real-Time Dispatch Console</h1>
        <p>Operational AI Predictors, Customer RFM Segmentation, Restaurant Operations Indices, and Real-Time Streaming Simulations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # We will use Streamlit Tabs inside Page 5
    tab_pred, tab_rfm, tab_rest, tab_sim = st.tabs([
        "🔮 Delivery Speed Predictor", 
        "👥 Customer RFM Clusters", 
        "🏅 Restaurant Operations Index", 
        "📡 Live Dispatch Simulator"
    ])
    
    # --- TAB 1: DELIVERY SPEED PREDICTOR ---
    with tab_pred:
        st.markdown("### 🔮 Operational Delivery ETA Predictor")
        st.markdown("Select details to predict transit delays using our operations scoring algorithm:")
        
        pred_col1, pred_col2 = st.columns(2)
        with pred_col1:
            sel_area = st.selectbox("Select Zone Location", all_areas, key="pred_area")
            sel_rest = st.selectbox("Select Restaurant Brand", all_restaurants, key="pred_rest")
        with pred_col2:
            sel_hour = st.slider("Select Order Hour (24h)", 0, 23, 19, key="pred_hour")
            sel_wknd = st.checkbox("Is it a Weekend? (Friday-Sunday)", value=True, key="pred_wknd")
            
        if st.button("🔮 Calculate Estimated Delivery ETA"):
            # Operations Math derived from our data simulation
            eta = 20
            
            # Area factor
            area_delays = {
                "Indiranagar": 0, "Koramangala": 2, "HSR Layout": 1, 
                "Whitefield": 12, "Jayanagar": -2, "Marathahalli": 9, 
                "BTM Layout": 3, "Malleshwaram": 0
            }
            eta += area_delays.get(sel_area, 0)
            
            # Hour factor
            hour_delay = 0
            if 12 <= sel_hour <= 14:
                hour_delay = 10 # Lunch hour
            elif 19 <= sel_hour <= 22:
                hour_delay = 18 # Dinner hour
            eta += hour_delay
            
            # Weekend factor
            if sel_wknd:
                eta += 6
                
            # Random fleet density variance
            variance = np.random.randint(-3, 4)
            eta += variance
            
            eta = max(15, eta) # minimum cap
            delay = max(0, eta - 30) # Delay beyond standard 30 min target
            
            # Render ETAs beautifully
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric(label="Predicted Delivery ETA", value=f"{eta} minutes")
                if eta <= 30:
                    st.success("✅ On-Time Delivery Expected (Meets 30-min Target)")
                elif 30 < eta <= 45:
                    st.warning("⚠️ Moderate Operational Delay Expected")
                else:
                    st.error("🚨 High Congestion Delay Warning!")
            with res_col2:
                st.metric(label="Calculated Delay Beyond Target (30m)", value=f"{delay} minutes")
                st.info(f"Rider dispatch route optimized for {sel_area} zone.")

    # --- TAB 2: CUSTOMER RFM CLUSTERS ---
    with tab_rfm:
        st.markdown("### 👥 Relational RFM Customer Segmentation")
        st.markdown("An RFM model groups customers based on Recency (how recently they ordered), Frequency (total orders), and Monetary (total spend) scores:")
        
        # Calculate live RFM metrics
        cust_rfm = df_full.groupby('customer_id').agg(
            frequency=('order_id', 'count'),
            monetary=('order_value', 'sum')
        ).reset_index()
        
        # Segment deterministic logic
        def assign_rfm_segment(row):
            freq = row['frequency']
            money = row['monetary']
            if money >= 1200 and freq >= 4:
                return "Champions (VIP)"
            elif freq >= 3:
                return "Loyal Customers"
            elif money >= 700:
                return "Promising Buyers"
            else:
                return "Occasional/Low Spend"
                
        cust_rfm['segment'] = cust_rfm.apply(assign_rfm_segment, axis=1)
        
        rfm_dist = cust_rfm['segment'].value_counts().reset_index()
        rfm_dist.columns = ['Segment', 'Count']
        
        rfm_col1, rfm_col2 = st.columns([1, 1])
        with rfm_col1:
            fig_rfm = px.pie(
                rfm_dist,
                values='Count',
                names='Segment',
                title="Customer RFM Segmentation Breakdown",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_rfm.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_rfm, width='stretch')
            
        with rfm_col2:
            st.markdown("##### 👥 Customer Segment Definitions & Counts")
            st.dataframe(
                rfm_dist,
                column_config={
                    "Segment": st.column_config.TextColumn("Customer Segment"),
                    "Count": st.column_config.NumberColumn("Total Users")
                },
                hide_index=True,
                width='stretch'
            )
            st.caption("Active segment analysis automatically drives targeted promo-code push notifications.")

    # --- TAB 3: RESTAURANT OPERATIONS INDEX ---
    with tab_rest:
        st.markdown("### 🏅 Composite Restaurant Performance Score Leaderboard")
        st.markdown("Calculates a composite score (0-100) based on: Ratings (40%), Total Revenue Volume (20%), Average Speed Efficiency (20%), and Cancellation Penalties (20%):")
        
        # Build restaurant scores
        rest_metrics = df_full.groupby('restaurant_name').agg(
            orders=('order_id', 'count'),
            revenue=('order_value', 'sum'),
            rating=('rating', 'mean'),
            time=('delivery_time', 'mean'),
            cancels=('order_status', lambda x: (x == 'Cancelled').sum())
        ).reset_index()
        
        # Calculate indicators
        rest_metrics['rating_score'] = (rest_metrics['rating'] / 5.0) * 100
        rest_metrics['cancel_pct'] = (rest_metrics['cancels'] / rest_metrics['orders']) * 100
        rest_metrics['cancel_score'] = (1.0 - (rest_metrics['cancels'] / rest_metrics['orders'])) * 100
        
        # Normalize Revenue (0 to 100)
        max_rev = rest_metrics['revenue'].max()
        min_rev = rest_metrics['revenue'].min()
        rest_metrics['rev_score'] = ((rest_metrics['revenue'] - min_rev) / (max_rev - min_rev)) * 100
        
        # Normalize Speed (faster = better, 0 to 100)
        max_time = rest_metrics['time'].max()
        min_time = rest_metrics['time'].min()
        rest_metrics['speed_score'] = (1.0 - ((rest_metrics['time'] - min_time) / (max_time - min_time))) * 100
        
        # Composite Score
        rest_metrics['composite_score'] = (
            rest_metrics['rating_score'] * 0.40 + 
            rest_metrics['rev_score'] * 0.20 + 
            rest_metrics['speed_score'] * 0.20 + 
            rest_metrics['cancel_score'] * 0.20
        ).round(1)
        
        rest_leaderboard = rest_metrics[['restaurant_name', 'composite_score', 'rating', 'time', 'cancel_pct']].sort_values(by='composite_score', ascending=False)
        
        # Display progress leaderboard
        for idx, row in rest_leaderboard.iterrows():
            name = row['restaurant_name']
            score = row['composite_score']
            star = row['rating']
            speed = row['time']
            cancel = row['cancel_pct']
            
            st.markdown(f"**{name}** — Score: `{score}/100` (★ {star:.2f} | ⏱️ {speed:.1f}m | ❌ {cancel:.1f}% cancels)")
            st.progress(float(score / 100.0))
            st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # --- TAB 4: LIVE DISPATCH SIMULATOR ---
    with tab_sim:
        st.markdown("### 📡 Live Real-Time Operations Dispatch Console")
        st.markdown("Simulate a live delivery control room. Start the streamer to watch orders log into our database in real-time!")
        
        import time
        import random
        
        sim_active = st.checkbox("📡 Turn On Live Order Streamer")
        
        placeholder = st.empty()
        
        if sim_active:
            # We simulate 10 incoming orders streaming onto the page
            simulation_log = []
            
            # Fixed anchors
            rest_names = list(df_full['restaurant_name'].unique())
            areas_list = list(df_full['delivery_area'].unique())
            partner_list = [f"DP_{100 + i}" for i in range(1, 20)]
            items_list = ["Chicken Biryani", "Butter Chicken & Naan", "Masala Dosa", "Margherita Pizza", "Hakka Noodles", "Burger & Fries"]
            
            for o_idx in range(1, 7):
                new_id = f"OD_LIVE_{1000 + o_idx}"
                selected_r = random.choice(rest_names)
                selected_a = random.choice(areas_list)
                selected_i = random.choice(items_list)
                val = random.randint(150, 580)
                status = random.choices(["Delivered", "Cancelled", "Rider Picked Up", "Preparing Food"], weights=[0.6, 0.05, 0.2, 0.15])[0]
                
                # Append to our local tracker
                simulation_log.insert(0, {
                    "Order ID": new_id,
                    "Restaurant": selected_r,
                    "Location Zone": selected_a,
                    "Food Ordered": selected_i,
                    "Order Value": f"₹{val}",
                    "Courier Agent": random.choice(partner_list),
                    "Live Status": status
                })
                
                # Render inside our placeholder
                with placeholder.container():
                    st.success(f"⚡ Live Order Received: {new_id} - {selected_i} from {selected_r}!")
                    st.dataframe(
                        pd.DataFrame(simulation_log),
                        width='stretch'
                    )
                
                # Sleep between live dispatches
                time.sleep(1.8)
                
            st.success("✅ Real-Time Dispatch session stream ended. Toggle off and on to restart.")
        else:
            st.info("Check the streaming simulator checkbox above to start the real-time dispatch dashboard.")
