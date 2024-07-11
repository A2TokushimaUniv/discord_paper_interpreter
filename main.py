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
from src.lang import FAIL_MESSAGES, WAIT_MESSAGES, RESULTS_MESSAGES, get_thread_name

load_dotenv()
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DATA_FOLDER_NAME = "paper"
DISCORD_RESPONSE_LIMIT = 2000
LANG = os.environ.get("RESPOND_LANG", "ja")


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    def _get_url_list(self, message):
        url_list = []
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        urls = re.findall(pattern, message.content)
        # URL from text message
        if urls:
            for url in urls:
                url_list.append({"url": url.strip(), "is_upload": False})
        # URL from file attachments
        for attachment in message.attachments:
            url_list.append({"url": attachment.url.strip(), "is_upload": True})
        return url_list

    async def on_message(self, message):
        is_dm = isinstance(message.channel, discord.DMChannel)
        # ignore bot own messages.
        if message.author == self.user:
            return
        # ignore if there is no mention when the message is not a DM.
        if not is_dm and client.user not in message.mentions:
            return

        url_list = self._get_url_list(message)
        mention = message.author.mention
        if is_dm:
            dest = message.channel
        else:
            # create thread for response summary
            dest = await message.create_thread(
                name=get_thread_name(url_list[0]["url"][:50], LANG),
                auto_archive_duration=60,
            )

        if not url_list:
            logger.warning("User doesn't specify url.")
            await respond(
                dest,
                mention,
                FAIL_MESSAGES["UploadNotPDF"][LANG],
            )
            return

        image_save_paths = []
        if not os.path.exists(DATA_FOLDER_NAME):
            try:
                os.makedirs(DATA_FOLDER_NAME)
            except Exception as e:
                print(f"Failed to make tmp folder: {e}")

        # response summary for each url
        for url_dic in url_list:
            tmp_pdf_file_name = (
                f"paper_{str(uuid.uuid4())}_{os.path.basename(url_dic['url'])}"
            )
            pdf_save_path = os.path.join(DATA_FOLDER_NAME, tmp_pdf_file_name)
            await respond(dest, mention, WAIT_MESSAGES["Reading"][LANG])
            is_success = download_pdf(
                url_dic["url"], url_dic["is_upload"], pdf_save_path
            )

            if is_success:
                paper_text, image_save_paths = read(DATA_FOLDER_NAME, pdf_save_path)
                prompt = create_prompt(paper_text)
                await respond(dest, mention, WAIT_MESSAGES["Generating"][LANG])
                answer = generate(prompt)
                response = f"{RESULTS_MESSAGES['Result'][LANG]}\n{answer}\n\n"[
                    :DISCORD_RESPONSE_LIMIT
                ]
                await respond(
                    dest,
                    mention,
                    response,
                    files=image_save_paths,
                )
                continue
            else:
                await respond(dest, mention, FAIL_MESSAGES["CannotReadPaper"][LANG])
                continue

        remove_tmp_files(pdf_save_path, image_save_paths)
        logger.info("Successfully send response.")


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
