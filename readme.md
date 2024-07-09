# discord_paper_interpreter

論文 PDF を読み取り要約を返してくれる Discord ボット

<img src="./example.png" title="example">

## 実行方法

- [開発者ポータル](https://discord.com/developers/applications)から Discord ボットを新規作成し、Discord トークンを得る
  - 参考：[Bot を作る - discordpy-japan](https://scrapbox.io/discordpy-japan/Bot%E3%82%92%E4%BD%9C%E3%82%8B)
- `.env`ファイルを作成し環境変数を格納する
  - MODEL は`GPT3`(`gpt-3.5-turbo`), `GPT4`(`gpt-4-turbo`), `GPT4o`(`gpt-4o`)からを選択する
  - RESPOND_LANG は`ja`か`en`から選択する

```.env
OPEN_AI_API_KEY=xxxxx
MODEL=GPT4o
DISCORD_BOT_TOKEN=xxxxx
RESPOND_LANG=ja
```

- `docker compose up`でボットを起動する
- ボット宛てに、論文 PDF の URL もしくはローカルの PDF をアップロードすると、要約が返ってくる

## 要約形式

- `data/format.txt`の形式で論文が要約されます.

## 注意事項

論文全文を読み取り、トークン数の多い ChatGPT モデルに入力しています.

利用料金には十分気を付けてください.
