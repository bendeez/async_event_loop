import AsyncLoop
from AsyncLoop import AsyncClient


async def scrape_other_website():
    results = await AsyncLoop.gather(*[AsyncClient.request("https://youtube.com") for _ in range(10)])
    return results

async def scrape_website(url):
    first_result = await scrape_other_website()
    print(first_result)
    second_result = await AsyncLoop.gather(*[AsyncClient.request(url) for _ in range(20)])
    return second_result

async def main():
    url = "https://github.com/"
    task_1 = AsyncLoop.create_task(scrape_website(url))
    print(task_1)
    task_2 = AsyncLoop.create_task(scrape_other_website())
    print(task_2)
    result = await AsyncLoop.gather(task_1,task_2)
    print(result)

AsyncLoop.run(main(), max_clients=100)
