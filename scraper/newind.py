import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def get_nie_headlines():
    url = "https://www.newindianexpress.com/topic/delhi-crime"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        md = result.markdown

        # Work only on the section after '# Delhi crime'
        block = md.split("# Delhi crime", 1)[-1]

        # Find all lines like: ###### [HEADLINE](link)
        pattern = re.findall(r"^###### \[(.*?)\]", block, re.MULTILINE)
        headlines = pattern.findall(md)
        return headlines[:10]

        # for idx, hl in enumerate(headlines[:10], 1):
        #     print(f"{idx}. {hl}")

if __name__ == "__main__":
    import asyncio
    headlines = asyncio.run(get_nie_headlines())
    for idx, headline in enumerate(headlines, 1):
        print(f"{idx}. {headline}")
