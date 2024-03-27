from logzero import logger
import os
from .utils import load_env

load_env()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")


def _add_mention(message, content):
    return f"{message.author.mention}\n{content}"



async def respond(message, content, files=[]):
    try:
        await message.channel.send(_add_mention(message, content), files=files[:10])
    except Exception as e:
        logger.warning(f"Failed to respond. text={content}")
        logger.warning(f"Exception: {e}")
    return