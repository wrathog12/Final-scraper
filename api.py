from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import urllib.parse
from datetime import datetime
import pytz

app = FastAPI(title="News API", description="API to fetch top 20 formatted news items from MongoDB")

# Load environment variables
load_dotenv()
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")

# Create MongoDB URI
uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)
db = client["news_db"]
processed_collection = db["Processed"]

def parse_gmt_date(date_str):
    """Parse GMT date string to datetime for sorting."""
    try:
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=pytz.UTC)
    except ValueError as e:
        print(f"⚠️ Error parsing date '{date_str}': {e}")
        return datetime.min.replace(tzinfo=pytz.UTC)  # Fallback for sorting

@app.get("/news", response_model=list[dict])
async def get_top_news():
    """Fetch the top 20 formatted news items, sorted by date descending."""
    try:
        # Fetch top 20 documents, sorted by date (descending)
        cursor = processed_collection.find().sort([("date", -1)]).limit(20)
        news_items = []
        
        for item in cursor:
            # Convert ObjectId to string for JSON serialization
            item_dict = item.copy()
            item_dict["_id"] = str(item_dict["_id"])
            # Ensure date is a string (already is, but for consistency)
            item_dict["date"] = item_dict.get("date", "")
            news_items.append(item_dict)
        
        # Sort in Python to handle string-to-datetime conversion
        news_items.sort(key=lambda x: parse_gmt_date(x["date"]), reverse=True)
        
        if not news_items:
            raise HTTPException(status_code=404, detail="No news items found in processed collection")
        
        return news_items
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.on_event("shutdown")
def close_mongo_connection():
    """Close MongoDB connection when app shuts down."""
    client.close()
    print("✅ MongoDB connection closed.")