import aiohttp
import asyncio

URL = "http://10.95.27.163/"


async def get_url_data(url, session):
    r= await session.request("GET", url=url)
    text = await r.text()
    print(text)
    return text


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(100):
            tasks.append(get_url_data(url=URL, session=session))

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
