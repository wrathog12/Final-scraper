import re
from crawl4ai import AsyncWebCrawler

async def get_ndtv():
    url = "https://www.ndtv.com/topic/delhi-crime-news"

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        markdown = result.markdown

        # Regex: Matches lines starting with ###  [Headline](Link)
        pattern = re.compile(r'^###  \[([^\]]+)\]\([^)]+\)', re.MULTILINE)
        headlines = pattern.findall(markdown)

        return headlines[:10]  # Always return, do not print

# Optional: Standalone test
if __name__ == "__main__":
    import asyncio
    headlines = asyncio.run(get_ndtv())
    for idx, headline in enumerate(headlines, 1):
        print(f"{idx}. {headline}")
