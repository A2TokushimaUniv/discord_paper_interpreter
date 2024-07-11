from logzero import logger
import discord

DISCORD_RESPONSE_LIMIT = 2000


async def respond(dest, mention, content, files=[]):
    send_files = []
    if files:
        for file in files[:10]:
            send_files.append(discord.File(file))

    response = f"{mention}\n{content}"[:DISCORD_RESPONSE_LIMIT]
    try:
        await dest.send(response, files=send_files)
    except Exception as e:
        logger.warning(f"Failed to respond. text={content}")
        logger.warning(f"Exception: {e}")
    return
