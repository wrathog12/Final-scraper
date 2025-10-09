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
    result = db[coll_name].delete_many({})
    print(f"🗑️ Cleared {result.deleted_count} documents from '{coll_name}'")
