SYSTEM_PROMPT = {
    "ja": "あなたはAIに関する研究を行っている専門家です。",
    "en": "You are an expert in research on AI.",
}

FAIL_MESSAGES = {
    "RequestFail": {
        "ja": "ChatGPTへのリクエストが失敗しました。\nタイムアウトになっているか、OpenAI APIのRateLimitに引っかかっている可能性があります。少し待ってから論文URLを再送してみてください。",
        "en": "Your request to ChatGPT failed. \nIt may have timed out or been stuck in the RateLimit of the OpenAI API. Please wait a bit and try resending the paper URL.",
    },
    "PaperSizeFail": {
        "ja": "論文の文章量が大きすぎたため、要約できませんでした。",
        "en": "The amount of text in the paper was too large to summarize.",
    },
    "UploadNotPDF": {
        "ja": "論文PDFのURLを送信するか、PDFをアップロードしてください。",
        "en": "Send us the URL of the PDF of your paper or upload the PDF.",
    },
    "CannotReadPaper": {
        "ja": "論文を正しく読み取ることができませんでした。",
        "en": "Could not read the paper correctly.",
    },
}

WAIT_MESSAGES = {
    "Reading": {"ja": "論文を読み取っています。", "en": "Reading the paper..."},
    "Generating": {
        "ja": "要約を生成中です。\n1~5分ほどかかります。",
        "en": "Generating summary is in progress. \nIt will take about 1~5 minutes.",
    },
}

RESULTS_MESSAGES = {
    "Result": {"ja": "要約は以下になります。", "en": "Here is summary."}
}


def get_thread_name(url, lang):
    if lang == "ja":
        return f"{url}の要約結果"
    else:
        return f"Summary of {url}"
