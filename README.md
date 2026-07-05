# AI-Powered News Scraper & Deduplicator

An intelligent news aggregation pipeline that scrapes multiple news portals, processes the unstructured data using Large Language Models (LLMs), deduplicates the content, and stores it systematically in a MongoDB database. 

## 🚀 Key Features

* **Multi-Portal Scraping:** Utilizes custom parsers (`gparser`) and `crawl4ai` to fetch the latest news from sources like NDTV, Indian Express, India TV, and Reddit based on specific keyword searches.
* **LLM-Powered Structuring:** Integrates Google's Generative AI (`gemma-3-27b-it`) to parse raw headlines and extract structured JSON data, inferring metadata such as "Crime Type" and specific "Location" (e.g., Delhi localities).
* **Robust Deduplication:**
  * **Timestamp Matching:** Ensures temporal uniqueness to prevent saving the same article fetched during different polling cycles.
  * **Semantic Deduplication:** Prevents fundamentally identical news stories from different sources from cluttering the database.
* **Database Management:** Built-in scripts to cleanly manage, verify, and clear the MongoDB instance.

## 📂 Directory Structure

```text
Final-scraper/
├── .gitignore
├── api.py                  # API endpoints (if exposing the scraped data)
├── check_data_db.py        # Utility to verify data integrity in MongoDB
├── clear_db.py             # Utility to flush the database
├── llm_original.py         # Handles LLM prompt building, batching, and parsing
├── main.py                 # Primary entry point for the scraping/processing pipeline
├── requirements.txt        # Python dependencies
└── scraper/                # Source-specific scraping modules
    ├── __init__.py
    ├── gparser.py          # Core parser handling keyword-based fetching
    ├── indianexp.py        
    ├── indiatv.py          
    ├── ndtv.py             
    ├── newind.py           
    └── reddit.py
```
🛠️ Prerequisites
Python 3.11+ * MongoDB: A running local or remote MongoDB instance.

Google Gemini API Key: Required for the LLM structuring phase.

⚙️ Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd Final-scraper
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory and add your API credentials and Database URI:

Code snippet
GEMMA_API_KEY=your_google_gemma_api_key_here
MONGO_URI=your_mongodb_connection_string
💻 Usage
Run the main pipeline:
To trigger the scraping process, format the data via the LLM, deduplicate it, and save it to the database:

Bash
python main.py
Testing the LLM Parsing:
If you want to test the LLM batching and formatting logic in isolation:

Bash
python llm_original.py
Database Utilities:

To check the current state and record count in your database:

Bash
python check_data_db.py
To clear all existing records:

Bash
python clear_db.py
🧠 How the LLM Extraction Works
The system batches incoming headlines from gparser and sends them to the Gemma model. The LLM is prompted to return a strictly formatted JSON array containing:

title: Exact headline

date: Article date

url: Source URL

type: Inferred category (e.g., specific crime types)

location: Specific locality mentioned in the text

The parser automatically strips markdown formatting from the response, validates the JSON, and assigns a unique UUID before passing it to the deduplication and database layers.

👤 Author
Abhishek Choudhary
