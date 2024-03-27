import discord
import re
from logzero import logger
from src.bot import(
    respond
)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        url_list = []
        urls = re.findall(pattern, message.content)
        if urls:
            for url in urls:
                url_list.append({"url": url, "is_discord_upload": False})


        if not url_list:
            logger.warning("User doesn't specify url.")
            await respond(message, "論文PDFのURLを指定してください。")
            return

        await respond(message, url_list)



intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run()