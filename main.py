from agent.search_agent import search


async def main():
    result = await search("")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
