import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def get_indianexp():
    url = "https://indianexpress.com/about/delhi-crime/"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        md = result.markdown

        # Extract the part after '## DELHI CRIME NEWS'
        block = md.split("## DELHI CRIME NEWS", 1)[-1]

        # Find all lines that start with '### ['
        pattern = re.findall(r"^###\s*\[(.*?)\]", block, re.MULTILINE)
        headlines = pattern.findall(md)
        return headlines[:10]  # Return only the first 10 headlines

        # for idx, hl in enumerate(headlines[:10], 1):
        #     print(f"{idx}. {hl}")

if __name__ == "__main__":
    import asyncio
    headlines = asyncio.run(get_indianexp())
    for idx, headline in enumerate(headlines, 1):
        print(f"{idx}. {headline}")
