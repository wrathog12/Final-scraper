from pymongo import MongoClient
import os
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime
from pprint import pprint

# Load environment variables
load_dotenv()

# Credentials
user = os.getenv("MONGO_USER")
password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
cluster = os.getenv("MONGO_CLUSTER")
uri = f"mongodb+srv://{user}:{password}@{cluster}/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)
db = client["news_db"]

# Collections
collections = ["raw collection", "Processed"]

for coll_name in collections:
    collection = db[coll_name]
    print(f"\n🔹 Collection: '{coll_name}'")

    # 1. Total number of documents
    total_count = collection.count_documents({})
    print(f" Total documents: {total_count}")

    # 2. Check for duplicates based on 'url'
    pipeline = [
        {"$group": {"_id": "$url", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}}
    ]
    duplicates = list(collection.aggregate(pipeline))
    print(f"🔁 Duplicate URLs: {len(duplicates)}")
    if duplicates:
        print("Top duplicate URLs:")
        for dup in duplicates[:5]:
            print(f"   - {dup['_id']} (x{dup['count']})")

    # 3. Top 10 most recent documents (assuming 'date' is string or datetime)
    print("\n Top 10 most recent entries:")
    try:
        top_docs = collection.find().sort("date", -1).limit(10)
        for i, doc in enumerate(top_docs, 1):
            print(f"{i}. {doc.get('title')} ({doc.get('date')}) [Type: {doc.get('type')}] [Location: {doc.get('location')}] [URL: {doc.get('url')}]")
    except Exception as e:
        print(" Could not sort by 'date':", e)



