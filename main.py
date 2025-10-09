import os
import uuid
import time
from dotenv import load_dotenv
from datetime import datetime
import json
import pymongo
import google.generativeai as genai
from pymongo import MongoClient
from scraper import gparser
import urllib.parse
from pymongo.errors import BulkWriteError
import asyncio
from datetime import datetime


# ---- Load Environment Variables ----
load_dotenv()
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

if not GEMMA_API_KEY:
    raise Exception("Gemma API key not found in .env (GEMMA_API_KEY)")


genai.configure(api_key=GEMMA_API_KEY)

# ---- MongoDB Setup ----
user = os.getenv("MONGO_USER")
password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
cluster = os.getenv("MONGO_CLUSTER")

# Create MongoDB URI
uri = f"mongodb+srv://{user}:{password}@{cluster}/?retryWrites=true&w=majority"

# Connect to the cluster
client = MongoClient(uri)
db = client["news_db"]
raw_collection = db["raw collection"]
processed_collection = db["Processed"]

BATCH_SIZE = 2
MODEL_NAME = "gemma-3-27b-it"
RATE_LIMIT_DELAY = 2.0

def build_prompt(batch):
    prompt = (
        "For each news item below, extract these fields as a JSON object:\n"
        "-title: a rephrased, concise, and clear version of the headline, preserving key details (e.g., crime type, location) in a standardized format (e.g., 'Delhi Police: [Crime Type] in [Location]')\n"
        "- date: the article's date\n"
        "- id: leave blank, to be filled by script\n"
        "- url: the url as provided\n"
        "- type: the main crime type (e.g., Murder, Robbery, etc) inferred from the headline. If not crime, set as 'N/A'.\n"
        "- location: the most specific Delhi locality mentioned, or 'Delhi' if not specified.\n"
        "Return a JSON array, only the array, no extra explanation.\n\n"
        "News items:\n"
    )
    for idx, item in enumerate(batch, 1):
        prompt += f"{idx}. '{item['title']}'\n   Date: {item['date']}\n   URL: {item['url']}\n"
    prompt += "\nReturn the array."
    return prompt

def parse_llm_response(response_text, batch):
    # Remove code fences if present
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    try:
        parsed = json.loads(response_text)
        if not isinstance(parsed, list):
            print("❌ LLM did not return a JSON array.")
            return []
        final = []
        for llm_item, orig_item in zip(parsed, batch):
            item = {
                "title": llm_item.get('title', orig_item['title']),
                "date": orig_item['date'],
                "id": str(uuid.uuid4()),
                "url": orig_item['url'],
                "type": llm_item.get('type', 'N/A'),
                "location": llm_item.get('location', 'Delhi') or 'Delhi'
            }
            # Check if the item is fully formatted (type and location are not empty or None)
            if item["type"] not in [None, "", "N/A"] and item["location"] not in [None, ""]:
                final.append(item)
            else:
                print(f"⚠️ Skipping item due to incomplete formatting: {item['title']} (type: {item['type']}, location: {item['location']})")
        return final
    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}\nRaw response:\n{response_text}\n")
        return []
    
def filter_duplicates(collection, items, key_fields):
    unique_items = []
    for item in items:
        query = {field: item.get(field) for field in key_fields}
        if not collection.find_one(query):
            unique_items.append(item)
        else:
            print(f"⚠️ Skipping duplicates.")
    return unique_items

def main():
    print("🔹 Fetching news headlines from gparser...")
    scraped_items = gparser.fetch_news()
    if not scraped_items:
        print("❗ No headlines found by gparser. Please check your scraper's output or date range.")
        return
    print(f"✅ {len(scraped_items)} headlines scraped.")
    
    print("🔹 Filtering duplicates for raw collection...")
    unique_raw_items = filter_duplicates(raw_collection, scraped_items, ["title", "url"])
    print(f"✅ {len(unique_raw_items)} unique raw items to store.")
    if unique_raw_items:
        print("🔹 Storing raw news items in MongoDB raw collection...")
        try:
            result = raw_collection.insert_many(unique_raw_items, ordered=False)
            print(f"✅{len(result.inserted_ids)} raw items stored in raw collection.")
        except pymongo.errors.BulkWriteError as bwe:
            print(f"⚠️ Some items were not inserted: {bwe.details['writeErrors']}")
            print(f"✅ {bwe.details['nInserted']} raw items stored in raw collection.")
    else:
        print("❗ No unique items to store in raw collection.")
    
    for i, item in enumerate(unique_raw_items, 1):
       print(f"{i}. {item['title']} ({item['date']}) [URL: {item['url']}]")


    model = genai.GenerativeModel(MODEL_NAME)
    formatted_results = []

    

    print(f"\n🔹 Sending news to Gemma in batches of {BATCH_SIZE}...")
    for i in range(0, len(unique_raw_items), BATCH_SIZE):
        batch = unique_raw_items[i:i+BATCH_SIZE]
        print(f"\n  ▶️ Processing batch {i//BATCH_SIZE+1} ({len(batch)} items)")
        # Print each item in the batch
        print("  --- Batch Items ---")
        for j, item in enumerate(batch, 1):
            print(f"  {j}. Title: {item['title']}")
            print(f"     Date: {item['date']}")

            print(f"     URL: {item['url']}")
            print("  " + "-" * 50)
        
        prompt = build_prompt(batch)
        print(f"  --- Prompt preview ---\n{prompt[:350]}...\n-----------------------")

        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 2048},
            )
            llm_text = getattr(response, "text", None) or getattr(response, "candidates", [{}])[0].get("content") or str(response)
            print(f"  --- Raw LLM Response ---\n{llm_text[:500]}...\n------------------------")
            batch_results = parse_llm_response(llm_text, batch)
            print(f"  ✅ Gemma returned {len(batch_results)} formatted items in this batch.")
            # Print formatted details for each item in batch_results
            print("  --- Formatted Results ---")
            for j, item in enumerate(batch_results, 1):
                print(f"  {j}. Title: {item['title']}")
                print(f"     Date: {item['date']}")
                print(f"     ID: {item['id']}")
                print(f"     URL: {item['url']}")
                print(f"     Type: {item['type']}")
                print(f"     Location: {item['location']}")
                print("  " + "-" * 50)
            formatted_results.extend(batch_results)
        except Exception as e:
            print(f"❌ Error calling Gemma: {e}")
        time.sleep(RATE_LIMIT_DELAY)

    if formatted_results:
     print("\n🔹 Filtering duplicates for processed collection...")
     unique_processed_items = filter_duplicates(processed_collection, formatted_results, ["title", "url"])
     print(f"✅ {len(unique_processed_items)} unique processed items to store.")
     if unique_processed_items:
        print("\n🔹 Storing fully formatted results in MongoDB processed collection...")
        try:
            result = processed_collection.insert_many(unique_processed_items)
            print(f"✅ {len(unique_processed_items)} formatted items stored in processed collection.")
        except pymongo.errors.BulkWriteError as bwe:
            print(f"⚠️ Some items were not inserted: {bwe.details['writeErrors']}")
            print(f"✅ {bwe.details['nInserted']} formatted items stored in processed collection.")
    else:
        print("❗ No unique items to store in processed collection.")
    # Store fully formatted results in MongoDB processed collection
    #if formatted_results:
        #print("\n🔹 Storing fully formatted results in MongoDB processed collection...")
        #processed_collection.insert_many(formatted_results)
        #print(f"✅ {len(formatted_results)} formatted items stored in processed collection.")
    
  # Replace the existing print loop in main()
    print("\n🔹 FORMATTED RESULTS:")
    if not formatted_results:
        print("❗ No items were fully formatted. Please check previous messages for errors.")
    else:
     for idx, item in enumerate(formatted_results, 1):
        # Convert ObjectId or any non-serializable fields to strings
        printable_item = item.copy()  # Create a copy to avoid modifying the original
        if '_id' in printable_item:
            printable_item['_id'] = str(printable_item['_id'])  # Convert ObjectId to string
        if 'id' in printable_item:
            printable_item['id'] = str(printable_item['id'])  # Ensure UUID is a string
        print(f"{idx}. {json.dumps(printable_item, ensure_ascii=False)}")

async def periodic_main(interval=3600):
    while True:
        print(f"\n[Scheduler] Running main() at {datetime.now()}")
        try:
            main()
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(periodic_main(3600))