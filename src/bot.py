from logzero import logger
import discord


def _add_mention(message, content):
    return f"{message.author.mention}\n{content}"


async def respond(message, content, files=[]):
    send_files = []
    if files:
        for file in files[:10]:
            send_files.append(discord.File(file))

    try:
        await message.channel.send(_add_mention(message, content), files=send_files)
    except Exception as e:
        logger.warning(f"Failed to respond. text={content}")
        logger.warning(f"Exception: {e}")
    return
