from logzero import logger
import discord


async def respond(dest, mention, content, files=[]):
    send_files = []
    if files:
        for file in files[:10]:
            send_files.append(discord.File(file))

    try:
        await dest.send(f"{mention}\n{content}", files=send_files)
    except Exception as e:
        logger.warning(f"Failed to respond. text={content}")
        logger.warning(f"Exception: {e}")
    return
