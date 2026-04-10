from agent.search_agent import search
from channels.feishu import WebSocketClient, LarkBot
from utils.message_queue import prompt_queue, reply_queue
from config import get_lark_config
from loguru import logger
import asyncio

config = get_lark_config()
reply_bot = LarkBot(config.app_id, config.app_secret)


async def _select():
    while True:
        await asyncio.sleep(3600)


async def consumer():
    session_filename = "gateway.jsonl"
    while True:
        item = await prompt_queue.get()  # Wait for item
        logger.info(f"Consumed {item}")
        result = await search(item.text, session_filename)
        logger.info(f"Reply {result}")
        reply_bot.send_text_message(item.chat_id, result, "chat_id")


def main():
    from lark_oapi.ws.client import loop

    client = WebSocketClient()
    client.start(loop)
    loop.create_task(consumer())
    loop.run_until_complete(_select())


if __name__ == "__main__":
    main()
