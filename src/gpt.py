import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from logzero import logger
from .utils import load_env

load_env()
# huge max tokens model
# https://platform.openai.com/docs/models
# gpt-4-32k is not available from OpenAI API
# https://help.openai.com/en/articles/7102672-how-can-i-access-gpt-4
MODEL_NAME = {"GPT3": "gpt-3.5-turbo", "GPT4": "gpt-4-turbo", "GPT4o": "gpt-4o"}
MODEL_MAX_TOKENS = {"GPT3": 16000, "GPT4": 128000, "GPT4o": 128000}
RESPONSE_MAX_TOKENS = 1000
model_env = os.environ.get("MODEL", "GPT3")
MODEL = model_env if model_env in list(MODEL_NAME.keys()) else "GPT3"
REQUEST_TIMEOUT = 300
SYSTEM_PROMPT = "あなたはAIに関する研究を行っている専門家です。"
openai.api_key = os.environ.get("OPENAI_API_KEY")


def create_prompt(paper_text):
    logger.info("Creating prompt...")
    # if user does'nt send format prompt of send blank files
    with open("./format.txt") as f:
        format_prompt = f.read()
    prompt = f"{format_prompt}\n\n{paper_text}\n\n"
    return prompt


def generate(prompt):
    chat = ChatOpenAI(
        model_name=MODEL_NAME[MODEL],
        temperature=0,  # Generate the same summary for the same papers.
        max_tokens=RESPONSE_MAX_TOKENS,
        request_timeout=REQUEST_TIMEOUT,
    )

    messages = [
        SystemMessage(SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    token_size = chat.get_num_tokens_from_messages(messages=messages)
    token_limit = MODEL_MAX_TOKENS[MODEL] - RESPONSE_MAX_TOKENS

    logger.info(f"Generating summary by {MODEL_NAME[MODEL]}...")
    if token_size <= token_limit:
        logger.info(
            f"The token size of the input to {MODEL_NAME[MODEL]} is {token_size}."
        )
        try:
            # WARNING: refactor to use LCEL
            response = chat(messages)
            response = response.content
        except Exception as e:
            logger.error("Failed to request to ChatGPT!")
            logger.error(f"Exception: {str(e)}")
            response = "ChatGPTへのリクエストが失敗しました。\nタイムアウトになっているか、OpenAI APIのRateLimitに引っかかっている可能性があります。少し待ってから論文URLを再送してみてください。"
    else:
        logger.warning("The token size is too large, so the tail is cut off.")
        response = "論文の文章量が大きすぎたため、要約できませんでした。"
    return response
