import discord
import re
from logzero import logger
from src.bot import respond
from src.utils import load_dotenv
from src.paper import download_pdf
from src.paper import read
from src.gpt import create_prompt, generate
from src.utils import remove_tmp_files
import os
import uuid

load_dotenv()
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TMP_FOLDER_NAME = "tmp"


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    def _get_url_list(self, message):
        url_list = []
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        urls = re.findall(pattern, message.content)
        # paper URL from text message
        if urls:
            for url in urls:
                url_list.append(url)
        # paper URL from file attachments
        attachments = message.attachments
        if attachments:
            for attachment in attachments:
                if attachment.filename.endswith(".pdf"):
                    url_list.append(attachment.url)
        return url_list

    async def on_message(self, message):
        is_dm = isinstance(message.channel, discord.DMChannel)
        # Ignore bot own messages.
        if message.author == self.user:
            return
        # Ignore if there is no mention when the message is not a DM.
        if not is_dm and client.user not in message.mentions:
            return

        url_list = self._get_url_list(message)
        mention = message.author.mention
        if is_dm:
            dest = message.channel
        else:
            dest = await message.create_thread(
                name=f"{url_list[0]}の要約結果", auto_archive_duration=60
            )

        if not url_list:
            logger.warning("User doesn't specify url.")
            await respond(dest, mention, "論文PDFのURLを指定してください。")
            return

        image_save_paths = []
        if not os.path.exists(TMP_FOLDER_NAME):
            try:
                os.makedirs(TMP_FOLDER_NAME)
            except Exception as e:
                print(f"Failed to make tmp folder: {e}")
        for url in url_list:
            tmp_pdf_file_name = f"paper_{str(uuid.uuid4())}_{os.path.basename(url)}"
            pdf_save_path = os.path.join(TMP_FOLDER_NAME, tmp_pdf_file_name)
            await respond(dest, mention, f"{url} から論文を読み取っています。")
            is_success = download_pdf(url, pdf_save_path)

            if is_success:
                paper_text, image_save_paths = read(TMP_FOLDER_NAME, pdf_save_path)
                prompt = create_prompt(paper_text)
                await respond(
                    dest, mention, "要約を生成中です。\n1~5分ほどかかります。\n"
                )
                answer = generate(prompt)
                await respond(
                    dest,
                    mention,
                    f"{url} の要約です。\n{answer}\n\n",
                    files=image_save_paths,
                )
            else:
                await respond(
                    dest,
                    mention,
                    f"{url} から論文を読み取ることができませんでした。",
                )
                return

        remove_tmp_files(pdf_save_path, image_save_paths)
        logger.info("Successfully send response.")


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
