🚀 Slack to Confluence Weekly Automation: System Spec
1. サービス概要 (Overview)
毎週火曜日 15:00 (JST) に自動起動し、過去7日間のSlackコミュニケーションを、Claude 3.5 Sonnet を介して「構造化された議事録」として Confluence に自動保存するシステム。

2. 実行スケジュール詳細
Trigger: GitHub Actions cron: '0 6 * * 2' (UTC 06:00 = JST 15:00)

Data Window: 実行時から過去168時間（7日間）

Output Destination: Confluence Cloud 指定スペース内のアーカイブ用階層

3. 実行プロセスの詳細
A. データ抽出 (Slack API)
conversations.history を使用し、oldest パラメータに 7日前 (now - 7days) のUnixタイムスタンプを指定。

各メッセージに対し thread_ts が存在する場合、conversations.replies を呼び出してスレッド内の議論をすべてマージ。

除外ルール: Botによる投稿 (subtype == 'bot_message') および特定のリアクション（例: :ignore:）が付与された投稿をスキップ。

B. インテリジェント要約 (Claude 3.5 Sonnet)
Input: 全メッセージのリスト（User Name, Timestamp, Content, Thread Level）

System Prompt: > あなたはプロフェッショナルな議事録作成者です。提供されたSlackログから「議論の背景」「決定事項」「ネクストアクション（担当者含む）」を抽出してください。

Output Format: Confluence Storage Format (XHTML)。

<h2>, <ul>, <li> を使用。

重要事項には <ac:structured-macro ac:name="info"> 等のConfluence固有マクロを使用。

C. ページ作成 (Confluence API)
Title: [Weekly_Log] {Channel_Name} ({YYYY/MM/DD})

Update Strategy: 同一タイトルのページが存在する場合は、既存ページをアーカイブし新規作成するか、バージョンアップを行う。

4. 具体的な実装コードの雛形 (Python)
Python
import os
import datetime
from slack_sdk import WebClient
from anthropic import Anthropic
from atlassian import Confluence

def main():
    # 1. タイムスタンプ計算 (7日前)
    now = datetime.datetime.now()
    oldest = (now - datetime.timedelta(days=7)).timestamp()

    # 2. クライアント初期化
    slack = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    claude = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    conf = Confluence(
        url=os.environ["CONF_URL"],
        username=os.environ["CONF_USER"],
        password=os.environ["CONF_TOKEN"]
    )

    # 3. メッセージ取得 (スレッド込み)
    logs = []
    res = slack.conversations_history(channel=os.environ["CHANNEL_ID"], oldest=oldest)
    for msg in res["messages"]:
        # メインメッセージ
        user_info = slack.users_info(user=msg.get('user'))
        user_name = user_info['user']['real_name']
        logs.append(f"[{user_name}]: {msg.get('text')}")
        
        # スレッド取得
        if "thread_ts" in msg:
            replies = slack.conversations_replies(channel=os.environ["CHANNEL_ID"], ts=msg["thread_ts"])
            for r in replies["messages"][1:]:
                r_user = slack.users_info(user=r.get('user'))['user']['real_name']
                logs.append(f"  - [{r_user}]: {r.get('text')}")

    # 4. Claudeで要約 (XHTML形式)
    prompt = f"以下のSlackログをConfluence用のHTML（Storage Format）形式で、決定事項とToDoを整理して要約してください:\n\n{''.join(logs)}"
    summary = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    ).content[0].text

    # 5. Confluenceへ投稿
    page_title = f"Weekly_{now.strftime('%Y%m%d')}"
    conf.create_page(
        space=os.environ["CONF_SPACE"],
        title=page_title,
        body=summary,
        representation='storage'
    )

if __name__ == "__main__":
    main()
5. API連携の手順とデプロイ
Slack App設定:

channels:history, groups:history, users:read の権限を持つBot Tokenを取得。

Confluence API設定:

Atlassian公式から「API Token」を発行。

GitHub Secretsの登録:

以下の環境変数をGitHubリポジトリのSecretsに保存。

SLACK_BOT_TOKEN, ANTHROPIC_API_KEY, CONF_URL, CONF_USER, CONF_TOKEN, CONF_SPACE, CHANNEL_ID