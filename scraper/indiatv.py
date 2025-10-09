import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def get_indiatv():
    url = "https://www.indiatvnews.com/topic/delhi-crime"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        # The markdown text
        md = result.markdown

        # Extract the relevant block after "# Delhi Crime"
        block = md.split("# Delhi Crime", 1)[-1]
        # Find all headlines that start with '###  [ ... ]'
        # We use a non-greedy match up to the first closing bracket
        pattern = re.findall(r"^###\s+\[\s*(.+?)\s*\]", block, re.MULTILINE)
        headlines = pattern.findall(md)
        return headlines[:10]  # Return only the first 10 headlines

        # # Get only the first 10
        # for idx, hl in enumerate(headlines[:10], 1):
        #     print(f"{idx}. {hl}")

if __name__ == "__main__":
    import asyncio
    headlines = asyncio.run(get_indiatv())
    for idx, headline in enumerate(headlines, 1):
        print(f"{idx}. {headline}")
