import os
import re
import pandas as pd
import numpy as np
from textblob import TextBlob

def run_analytics_pipeline():
    print("==============================================")
    print("[START] Starting Zomato/Swiggy Analytics Data Pipeline")
    print("==============================================")
    
    # 1. Check Paths
    raw_path = "data/raw_data.csv"
    cleaned_path = "data/cleaned_data.csv"
    
    if not os.path.exists(raw_path):
        print(f"[ERROR] Raw data file not found at {raw_path}. Please run generate_data.py first.")
        return
        
    # 2. Ingestion
    print(f"[STEP 1] Ingesting raw order logs from {raw_path}...")
    df = pd.read_csv(raw_path)
    initial_shape = df.shape
    print(f"   Initial shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # 3. Data Cleaning (Step 2 PRD Tasks)
    print("[STEP 2] Running Data Cleaning tasks...")
    
    # A. Remove Null values in critical identifier columns
    df = df.dropna(subset=['order_id'])
    df = df[df['customer_id'].notna() & (df['customer_id'].astype(str).str.strip() != "")]
    df = df[df['restaurant_name'].notna() & (df['restaurant_name'].astype(str).str.strip() != "")]
    
    # Drop rows where Completed (Delivered) orders are missing delivery times or ratings
    df = df[~((df['order_status'] == 'Delivered') & (df['delivery_time'].isnull()))]
    df = df[~((df['order_status'] == 'Delivered') & (df['rating'].isnull()))]
    
    # B. Remove Duplicate records
    df = df.drop_duplicates()
    
    # Convert numeric fields
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['delivery_time'] = pd.to_numeric(df['delivery_time'], errors='coerce')
    df['order_value'] = pd.to_numeric(df['order_value'], errors='coerce')
    
    # C. Remove Invalid ratings
    df = df[~((df['order_status'] == 'Delivered') & ((df['rating'] < 1) | (df['rating'] > 5)))]
    
    # D. Remove Negative delivery times
    df = df[~((df['order_status'] == 'Delivered') & (df['delivery_time'] < 0))]
    
    # E. Standardize areas and food categories
    df['delivery_area'] = df['delivery_area'].astype(str).str.strip().str.title()
    df['category'] = df['category'].astype(str).str.strip().str.title()
    
    # F. Standardize time formats
    df['order_time'] = pd.to_datetime(df['order_time'])
    
    print(f"   Shape after filters: {df.shape[0]} rows (Removed {initial_shape[0] - df.shape[0]} anomalous records)")
    
    # 4. Feature Engineering
    print("[STEP 3] Running Temporal Feature Engineering...")
    df['order_date'] = df['order_time'].dt.date
    df['order_hour'] = df['order_time'].dt.hour
    df['order_day'] = df['order_time'].dt.day_name()
    df['order_day_name'] = df['order_day'] # Alias for backwards compatibility
    df['order_day_of_week'] = df['order_time'].dt.dayofweek
    
    # Weekend flag (Friday, Saturday, Sunday)
    df['is_weekend'] = df['order_day_of_week'].isin([4, 5, 6]).astype(int)
    
    # Peak hour classification
    def get_peak_label(hour):
        if 12 <= hour <= 14:
            return 'Lunch Peak'
        elif 19 <= hour <= 22:
            return 'Dinner Peak'
        else:
            return 'Off-Peak'
            
    df['peak_hour_label'] = df['order_hour'].apply(get_peak_label)
    
    # G. Create delivery delay column (target time = 30 minutes)
    df['delivery_delay'] = df['delivery_time'].apply(lambda x: max(0, x - 30) if pd.notnull(x) else np.nan)
    
    print("   Created columns: delivery_delay, order_hour, order_day")
    
    # 5. Sentiment Analysis (NLP)
    print("[STEP 4] Running NLP Customer Review Sentiment Analysis...")
    
    # A. Clean text comments
    def clean_raw_review(text):
        if pd.isnull(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    df['clean_review'] = df['review'].apply(clean_raw_review)
    
    # B. Purge stopwords (standard + industry neutrals)
    from nltk.corpus import stopwords
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set(["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
                          "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "what", 
                          "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
                          "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", 
                          "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", 
                          "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", 
                          "between", "into", "through", "during", "before", "after", "above", "below", 
                          "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", 
                          "further", "then", "once", "here", "there", "when", "where", "why", "how", 
                          "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", 
                          "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", 
                          "can", "will", "just", "should", "now"])
                          
    industry_neutrals = ["food", "order", "ordered", "restaurant", "delivery", "partner", "delivered", "placed"]
    stop_words.update(industry_neutrals)
    
    def purge_stopwords(text):
        words = text.split()
        filtered_words = [w for w in words if w not in stop_words]
        return " ".join(filtered_words)
        
    df['clean_review_no_stop'] = df['clean_review'].apply(purge_stopwords)
    
    # C. Calculate TextBlob metrics
    def get_polarity(text):
        if not text:
            return 0.0
        return TextBlob(str(text)).sentiment.polarity
        
    def get_subjectivity(text):
        if not text:
            return 0.0
        return TextBlob(str(text)).sentiment.subjectivity
        
    df['sentiment_polarity'] = df['clean_review_no_stop'].apply(get_polarity)
    df['sentiment_subjectivity'] = df['clean_review_no_stop'].apply(get_subjectivity)
    
    def classify_sentiment(polarity):
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
            
    df['sentiment_category'] = df['sentiment_polarity'].apply(classify_sentiment)
    
    # Log distribution
    dist = df['sentiment_category'].value_counts()
    print("   Calculated sentiment metrics:")
    for cat, val in dist.items():
        print(f"      - {cat}: {val} orders ({val/len(df)*100:.1f}%)")
        
    # Correlation Check
    delivered_df = df[df['order_status'] == 'Delivered']
    corr = delivered_df['delivery_time'].corr(delivered_df['sentiment_polarity'])
    print(f"   Correlation (Delivery Time vs. Sentiment Polarity): {corr:.4f}")
    
    # 6. Database Normalization (Step 3 DDL)
    print("[STEP 5] Normalizing into 3 relational tables (customers, restaurants, orders)...")
    
    # A. Restaurants table extraction
    restaurants_data = [
        {"restaurant_id": "REST_01", "restaurant_name": "Spice Symphony", "category": "North Indian", "area": "Indiranagar"},
        {"restaurant_id": "REST_02", "restaurant_name": "The Golden Dosa", "category": "South Indian", "area": "Jayanagar"},
        {"restaurant_id": "REST_03", "restaurant_name": "Royal Biryani House", "category": "Biryani & Mughlai", "area": "Koramangala"},
        {"restaurant_id": "REST_04", "restaurant_name": "Wok & Roll", "category": "Chinese & Asian", "area": "Marathahalli"},
        {"restaurant_id": "REST_05", "restaurant_name": "Bella Italia", "category": "Italian", "area": "Indiranagar"},
        {"restaurant_id": "REST_06", "restaurant_name": "Burger Bistro", "category": "Fast Food", "area": "HSR Layout"},
        {"restaurant_id": "REST_07", "restaurant_name": "The Salad Bowl", "category": "Healthy & Salads", "area": "Whitefield"},
        {"restaurant_id": "REST_08", "restaurant_name": "Sweet Retreat", "category": "Desserts", "area": "BTM Layout"},
        {"restaurant_id": "REST_09", "restaurant_name": "Cafe Daybreak", "category": "Continental & Beverages", "area": "Malleshwaram"},
        {"restaurant_id": "REST_10", "restaurant_name": "Tandoori Nights", "category": "North Indian", "area": "Koramangala"},
    ]
    rest_df = pd.DataFrame(restaurants_data)
    rest_df.to_csv("data/restaurants_table.csv", index=False)
    print("   Exported data/restaurants_table.csv")

    # B. Customers table extraction
    unique_cust_ids = df['customer_id'].unique()
    first_names = ["Aarav", "Neha", "Rohan", "Aditya", "Priya", "Amit", "Anjali", "Suresh", "Ramesh", "Deepika", "Karan", "Simran", "Rahul", "Pooja", "Vikram"]
    last_names = ["Sharma", "Gupta", "Das", "Patel", "Singh", "Kumar", "Joshi", "Verma", "Sen", "Reddy", "Nair", "Mehta", "Iyer", "Rao", "Mishra"]
    
    customers_list = []
    # Seed for deterministic generation based on hash values
    for cust_id in unique_cust_ids:
        h = abs(hash(cust_id))
        f_name = first_names[h % len(first_names)]
        l_name = last_names[(h // len(first_names)) % len(last_names)]
        customers_list.append({
            "customer_id": cust_id,
            "customer_name": f"{f_name} {l_name}",
            "city": "Bengaluru"
        })
    cust_df = pd.DataFrame(customers_list)
    cust_df.to_csv("data/customers_table.csv", index=False)
    print("   Exported data/customers_table.csv")

    # C. Orders table extraction
    rest_mapping = {r["restaurant_name"]: r["restaurant_id"] for r in restaurants_data}
    orders_rel = pd.DataFrame()
    orders_rel["order_id"] = df["order_id"]
    orders_rel["customer_id"] = df["customer_id"]
    orders_rel["restaurant_id"] = df["restaurant_name"].map(rest_mapping)
    orders_rel["order_time"] = df["order_time"]
    orders_rel["delivery_time"] = df["delivery_time"]
    orders_rel["status"] = df["order_status"]
    orders_rel["rating"] = df["rating"]
    orders_rel["order_value"] = df["order_value"]
    orders_rel["food_item"] = df["food_item"]
    
    orders_rel.to_csv("data/orders_table.csv", index=False)
    print("   Exported data/orders_table.csv")
    
    # 7. Save output
    print(f"[STEP 6] Exporting cleaned & enriched data to {cleaned_path}...")
    df.to_csv(cleaned_path, index=False)
    print("[SUCCESS] Data Pipeline completed successfully! Ready for SQL & Streamlit.")
    print("==============================================")

if __name__ == "__main__":
    run_analytics_pipeline()
