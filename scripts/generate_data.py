import os
import random
import csv
from datetime import datetime, timedelta

def generate_dataset(num_records=5000):
    print(f"Generating {num_records} realistic food delivery records...")

    # Set random seed for reproducibility
    random.seed(42)

    # Base metadata pools
    areas = [
        "Indiranagar", "Koramangala", "HSR Layout", "Whitefield", 
        "Jayanagar", "Marathahalli", "BTM Layout", "Malleshwaram"
    ]
    
    # Area traffic multipliers (Whitefield & Marathahalli have higher traffic delays)
    area_delay_multipliers = {
        "Indiranagar": 1.0,
        "Koramangala": 1.1,
        "HSR Layout": 1.05,
        "Whitefield": 1.4, # High traffic
        "Jayanagar": 0.95,
        "Marathahalli": 1.3, # High traffic
        "BTM Layout": 1.15,
        "Malleshwaram": 1.0
    }

    restaurants_menu = {
        "Spice Symphony": {
            "category": "North Indian",
            "items": [
                ("Butter Chicken & Naan", 350),
                ("Paneer Butter Masala Meal", 320),
                ("Dal Makhani with Jeera Rice", 280),
                ("Tandoori Chicken Half", 380),
                ("Kadhai Paneer with Roti", 310)
            ]
        },
        "The Golden Dosa": {
            "category": "South Indian",
            "items": [
                ("Masala Dosa with Sambar", 120),
                ("Idli Vada Combo", 100),
                ("Rava Kesari & Dosa Combo", 150),
                ("Onion Uttapam", 130),
                ("Filter Coffee & Upma", 110)
            ]
        },
        "Royal Biryani House": {
            "category": "Biryani & Mughlai",
            "items": [
                ("Chicken Dum Biryani", 330),
                ("Mutton Biryani", 450),
                ("Veg Hyderabadi Biryani", 280),
                ("Egg Biryani", 260),
                ("Chicken Tikka Biryani", 360)
            ]
        },
        "Wok & Roll": {
            "category": "Chinese & Asian",
            "items": [
                ("Veg Hakka Noodles", 220),
                ("Chicken Fried Rice & Manchurian", 290),
                ("Schezwan Noodles", 230),
                ("Chilli Chicken Gravy", 280),
                ("Veg Spring Rolls (6 pcs)", 160)
            ]
        },
        "Bella Italia": {
            "category": "Italian",
            "items": [
                ("Margherita Pizza 10-inch", 380),
                ("Chicken Alfredo Pasta", 360),
                ("Veg Arrabiata Penne Pasta", 310),
                ("Farmhouse Veg Pizza", 420),
                ("Garlic Bread with Cheese", 150)
            ]
        },
        "Burger Bistro": {
            "category": "Fast Food",
            "items": [
                ("Classic Cheese Burger & Fries", 240),
                ("Crispy Chicken Burger", 210),
                ("Spicy Paneer Wrap", 180),
                ("Chicken Nuggets (9 pcs)", 190),
                ("Loaded Nachos", 220)
            ]
        },
        "The Salad Bowl": {
            "category": "Healthy & Salads",
            "items": [
                ("Caesar Salad", 240),
                ("Quinoa Avocado Salad", 320),
                ("High-Protein Chicken Salad", 290),
                ("Greek Salad", 230),
                ("Fresh Fruit Bowl", 180)
            ]
        },
        "Sweet Retreat": {
            "category": "Desserts",
            "items": [
                ("Chocolate Lava Cake", 140),
                ("Red Velvet Pastry", 150),
                ("Gulab Jamun (4 pcs)", 100),
                ("Sizzling Brownie", 180),
                ("Kulfi Falooda", 130)
            ]
        },
        "Cafe Daybreak": {
            "category": "Continental & Beverages",
            "items": [
                ("Club Sandwich", 210),
                ("Iced Latte", 160),
                ("Hot Chocolate", 170),
                ("Paneer Tikka Sandwich", 190),
                ("Classic Cold Coffee", 150)
            ]
        },
        "Tandoori Nights": {
            "category": "North Indian",
            "items": [
                ("Chicken Seekh Kebab", 310),
                ("Paneer Tikka", 280),
                ("Malai Kofta & Lachha Paratha", 330),
                ("Tandoori Roti Combo", 180),
                ("Butter Chicken Combo Meal", 360)
            ]
        }
    }

    restaurants = list(restaurants_menu.keys())

    # Delivery Partners
    partners = [f"DP_{100 + i}" for i in range(1, 101)] # 100 delivery partners

    # Review sentence pools based on ratings
    reviews_pool = {
        5: [
            "Amazing food, super fast delivery!",
            "Outstanding quality! Will definitely order again.",
            "Extremely satisfied, delivered hot and fresh!",
            "Best meal ever. Highly recommended!",
            "Delivered way before time, packaging was excellent!",
            "Perfect taste, clean packaging, and polite delivery partner."
        ],
        4: [
            "Good taste and neat packaging.",
            "Tasty food, but could be a bit warmer.",
            "Overall great experience. Prompt service.",
            "Satisfied with the delivery speed and quality.",
            "Decent portion size and good taste. Recommended.",
            "Tasty food, standard delivery. Satisfactory."
        ],
        3: [
            "Average food. Nothing special.",
            "Food was okay, but delivery took some time.",
            "Portion size was small for the price.",
            "Packaging could have been better. Average taste.",
            "Prompt delivery but taste was average.",
            "The food was decent but arrived a bit cold."
        ],
        2: [
            "Food was cold when it arrived.",
            "Too spicy, couldn't eat it. Disappointed.",
            "Delivery took almost an hour. Unhappy.",
            "Not worth the price, portion was very small.",
            "Taste was disappointing. Packaging was leaked.",
            "The item delivered was incorrect and lukewarm."
        ],
        1: [
            "Worst service! Delivered extremely late and completely cold.",
            "The food tasted stale and horrible! Threw it in the trash.",
            "Unprofessional delivery partner. Very bad experience.",
            "Missing items in my order and food was cold. Avoid this place!",
            "Terrible experience, food was completely spilled inside the bag.",
            "Awful experience! Delayed by over an hour and no response."
        ]
    }

    cancellation_reasons = [
        "Restaurant could not prepare food in time",
        "Delivery partner could not be assigned due to heavy rain",
        "Customer cancelled the order",
        "Delivery address was outside the delivery radius",
        "Item out of stock at restaurant"
    ]

    # Let's generate data covering the last 30 days
    start_date = datetime(2026, 4, 27, 0, 0, 0)
    
    orders = []

    for i in range(1, num_records + 1):
        order_id = f"OD{10000 + i}"
        customer_id = f"CUST{random.randint(2001, 3500)}"
        restaurant_name = random.choice(restaurants)
        rest_details = restaurants_menu[restaurant_name]
        category = rest_details["category"]
        
        # Pick food item
        food_item, base_price = random.choice(rest_details["items"])
        
        # Quantity (mostly 1, sometimes 2 or 3)
        qty = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
        order_value = base_price * qty
        
        # Add random add-ons/delivery fee to the order value
        delivery_fee = random.choice([20, 30, 40, 50])
        order_value += delivery_fee
        
        # Order status: Delivered (95%) vs Cancelled (5%)
        order_status = random.choices(["Delivered", "Cancelled"], weights=[0.95, 0.05])[0]
        
        # Order Time modeling (peak hours vs off-peak)
        # Random day in the last 30 days
        days_offset = random.randint(0, 29)
        # Select hour based on Zomato/Swiggy order hourly distribution
        # Lunch peak (12-14), Dinner peak (19-22) are most popular
        hour_weights = [
            1, 1, 0, 0, 0, 1, 3, 5, 4, 3, 3, 6, # 00:00 to 11:00
            14, 18, 12, 5, 4, 6, 12, 22, 28, 22, 10, 4 # 12:00 to 23:00
        ]
        order_hour = random.choices(range(24), weights=hour_weights)[0]
        order_minute = random.randint(0, 59)
        order_second = random.randint(0, 59)
        
        order_time = start_date + timedelta(
            days=days_offset, hours=order_hour, minutes=order_minute, seconds=order_second
        )
        
        delivery_area = random.choice(areas)
        delivery_partner = random.choice(partners)
        
        # Build logic for Delivery Time (only if Delivered)
        if order_status == "Delivered":
            # Base delivery time (15 - 28 mins)
            base_delivery = random.randint(15, 28)
            
            # Traffic/Area factor
            area_mult = area_delay_multipliers[delivery_area]
            
            # Hour factor (peak hours have heavier traffic & kitchen load)
            hour_delay = 0
            if 12 <= order_hour <= 14:
                hour_delay = random.randint(8, 15) # Lunch Peak
            elif 19 <= order_hour <= 22:
                hour_delay = random.randint(12, 22) # Dinner Peak
                
            # Day factor (Weekends Friday, Saturday, Sunday have slightly higher delay)
            day_delay = 0
            if order_time.weekday() in [4, 5, 6]: # Fri, Sat, Sun
                day_delay = random.randint(3, 10)
                
            # Random additional factors (e.g. weather, distance)
            random_factor = random.choices([0, 5, 10, 20], weights=[0.7, 0.18, 0.08, 0.04])[0]
            
            delivery_time = int((base_delivery + hour_delay + day_delay + random_factor) * area_mult)
            
            # Let's cap delivery time to a realistic range (15 - 85 mins)
            delivery_time = max(15, min(delivery_time, 85))
            
            # Modeling Rating based on delivery time and restaurant quality
            # Very fast delivery (< 25 min): higher chance of 5 stars
            # Very late delivery (> 45 min): higher chance of 1-2 stars
            if delivery_time < 25:
                rating = random.choices([5, 4, 3], weights=[0.75, 0.20, 0.05])[0]
            elif 25 <= delivery_time <= 40:
                rating = random.choices([5, 4, 3, 2], weights=[0.35, 0.45, 0.15, 0.05])[0]
            elif 40 < delivery_time <= 55:
                rating = random.choices([4, 3, 2, 1], weights=[0.15, 0.35, 0.35, 0.15])[0]
            else: # Delivery took > 55 mins! Very late!
                rating = random.choices([2, 1], weights=[0.20, 0.80])[0]
                
            review = random.choice(reviews_pool[rating])
        else:
            # Cancelled Order
            delivery_time = "" # Null/Empty
            rating = "" # Null/Empty
            review = random.choice(cancellation_reasons)
            
        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "restaurant_name": restaurant_name,
            "food_item": food_item,
            "category": category,
            "order_time": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "delivery_time": delivery_time,
            "delivery_area": delivery_area,
            "order_status": order_status,
            "rating": rating,
            "review": review,
            "order_value": order_value,
            "delivery_partner": delivery_partner
        })
        
    # Inject simulated data anomalies to test and showcase our Data Cleaning pipeline!
    print("Injecting simulated data anomalies for the cleaning pipeline to solve...")
    # 1. Add duplicates (approx 15 records)
    for idx in range(15):
        orders.append(orders[idx].copy())
        
    # 2. Add negative delivery times (5 records)
    for idx in range(5):
        bad_order = orders[idx * 10].copy()
        bad_order["order_id"] = f"OD_BAD_TIME_{idx}"
        bad_order["delivery_time"] = -random.randint(10, 45)
        bad_order["order_status"] = "Delivered"
        orders.append(bad_order)
        
    # 3. Add invalid ratings (5 records)
    for idx in range(5):
        bad_order = orders[idx * 12].copy()
        bad_order["order_id"] = f"OD_BAD_RATE_{idx}"
        bad_order["rating"] = random.choice([-1, 0, 9, 10])
        bad_order["order_status"] = "Delivered"
        orders.append(bad_order)
        
    # 4. Add non-standard area names (5 records)
    bad_areas = ["indiranagar  ", "  KORAMANGALA", "hsr layout", "whitefield  ", "btm layout"]
    for idx, area in enumerate(bad_areas):
        bad_order = orders[idx * 15].copy()
        bad_order["order_id"] = f"OD_BAD_AREA_{idx}"
        bad_order["delivery_area"] = area
        orders.append(bad_order)
        
    # 5. Add non-standard food categories (5 records)
    bad_cats = ["north indian", "ITALIAN", "chinese & asian", "desserts", "healthy & salads"]
    for idx, cat in enumerate(bad_cats):
        bad_order = orders[idx * 20].copy()
        bad_order["order_id"] = f"OD_BAD_CAT_{idx}"
        bad_order["category"] = cat
        orders.append(bad_order)
        
    # 6. Add empty/null values in critical fields (5 records)
    for idx in range(5):
        bad_order = orders[idx * 25].copy()
        bad_order["order_id"] = f"OD_BAD_NULL_{idx}"
        if idx % 2 == 0:
            bad_order["customer_id"] = ""
        else:
            bad_order["restaurant_name"] = ""
        orders.append(bad_order)

    # Write to raw_data.csv
    os.makedirs("data", exist_ok=True)
    csv_file_path = os.path.join("data", "raw_data.csv")
    
    headers = [
        "order_id", "customer_id", "restaurant_name", "food_item", "category",
        "order_time", "delivery_time", "delivery_area", "order_status", "rating",
        "review", "order_value", "delivery_partner"
    ]
    
    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(orders)
        
    print(f"Data generation complete! Saved to: {csv_file_path}")

if __name__ == "__main__":
    generate_dataset(5000)
