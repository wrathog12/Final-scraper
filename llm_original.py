import os
import uuid
import time
from dotenv import load_dotenv
from datetime import datetime

import google.generativeai as genai

from scraper import gparser

# ---- Load API Key ----
load_dotenv()
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")
if not GEMMA_API_KEY:
    raise Exception("Gemma API key not found in .env (GEMMA_API_KEY)")
genai.configure(api_key=GEMMA_API_KEY)

BATCH_SIZE = 2
MODEL_NAME = "gemma-3-27b-it"
RATE_LIMIT_DELAY = 2.0

def build_prompt(batch):
    prompt = (
        "For each news item below, extract these fields as a JSON object:\n"
        "- title: the exact headline\n"
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

import json
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
            final.append({
                "title": orig_item['title'],
                "date": orig_item['date'],
                "id": str(uuid.uuid4()),
                "url": orig_item['url'],
                "type": llm_item.get('type', 'N/A'),
                "location": llm_item.get('location', 'Delhi') or 'Delhi'
            })
        return final
    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}\nRaw response:\n{response_text}\n")
        return []

def main():
    print("🔹 Fetching news headlines from gparser...")
    scraped_items = gparser.fetch_news()
    if not scraped_items:
        print("❗ No headlines found by gparser. Please check your scraper's output or date range.")
        return
    print(f"✅ {len(scraped_items)} headlines scraped.")
    for i, item in enumerate(scraped_items[:3], 1):
        print(f" {i}. {item['title']} ({item['date']}) [URL: {item['url']}]")

    model = genai.GenerativeModel(MODEL_NAME)
    formatted_results = []

    print(f"\n🔹 Sending news to Gemma in batches of {BATCH_SIZE}...")
    for i in range(0, len(scraped_items), BATCH_SIZE):
        batch = scraped_items[i:i+BATCH_SIZE]
        prompt = build_prompt(batch)
        print(f"\n  ▶️ Processing batch {i//BATCH_SIZE+1} ({len(batch)} items)")
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
            formatted_results.extend(batch_results)
        except Exception as e:
            print(f"❌ Error calling Gemma: {e}")
        time.sleep(RATE_LIMIT_DELAY)

    print("\n🔹 FORMATTED RESULTS:")
    if not formatted_results:
        print("❗ No items were formatted. Please check previous messages for errors.")
    else:
        for idx, item in enumerate(formatted_results, 1):
            print(f"{idx}. {json.dumps(item, ensure_ascii=False)}")

    print(f"\n🟩 {len(formatted_results)} total formatted items.")

if __name__ == "__main__":
    main()
















#print(f"\n🔹 Sending news to Gemma in batches of {BATCH_SIZE}...")
    # for i in range(0, len(scraped_items), BATCH_SIZE):
    #     batch = scraped_items[i:i+BATCH_SIZE]
    #     prompt = build_prompt(batch)
    #     print(f"\n  ▶️ Processing batch {i//BATCH_SIZE+1} ({len(batch)} items)")

    #     try:
    #         response = model.generate_content(
    #             prompt,
    #             generation_config={"temperature": 0.2, "max_output_tokens": 2048},
    #         )
    #         llm_text = getattr(response, "text", None) or getattr(response, "candidates", [{}])[0].get("content") or str(response)
    #         print(f"  --- Raw LLM Response ---\n{llm_text[:500]}...\n------------------------")
    #         batch_results = parse_llm_response(llm_text, batch)
    #         print(f"  ✅ Gemma returned {len(batch_results)} formatted items in this batch.")
    #         formatted_results.extend(batch_results)
    #     except Exception as e:
    #         print(f"❌ Error calling Gemma: {e}")
    #     time.sleep(RATE_LIMIT_DELAY)

    # for i, item in enumerate(scraped_items[:3], 1):
    #     source = item.get('source', 'N/A')
    #     print(f"{i}. {item['title']} ({item['date']}) [Source: {source}] [URL: {item['url']}]")

    # model = genai.GenerativeModel(MODEL_NAME)
    # formatted_results = []
