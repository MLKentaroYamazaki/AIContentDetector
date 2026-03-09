# 仕様書：Slack → Confluence 週次メッセージ自動転記システム

## 概要

毎週火曜日15時に、指定Slackチャンネルからメッセージを抽出し、Confluenceページに自動出力するスクリプト。対象は「全社員向け」と「AIBAメンバー向け」の2チャンネル。

---

## 1. システム構成

```
[Slack API]
    ↓  (メッセージ取得)
[Python スクリプト: main.py]
    ↓  (整形・分類)
[Confluence API]
    ↓  (ページ作成 or 更新)
[Confluence: 週次レポートページ]
```

---

## 2. 対象チャンネル

| 対象             | Slack チャンネル名           | チャンネルID       | Confluence 出力先スペース         |
|------------------|------------------------------|--------------------|----------------------------------|
| 全社員向け       | `#all_nippon_mlgr`           | `CGVF155S7`        | スペースキー: `CD`               |
|                  | `#announcements-all`         | `C80JUUUMU`        | 親ページID: `2245722113`（要確認）|
| AIBAメンバー向け | `#aiba-all`                  | `C08LJCL2JTG`      | スペースキー: `CD`（要確認）      |
|                  | `#aiba-edx-all`              | `C0AK24S555F`      | 親ページID: `2245722113`（要確認）|

> **TODO**: 全社員向け・AIBA向けで親ページを分ける場合は、それぞれの親ページIDを設定すること。

---

## 3. 実行スケジュール

- **タイミング**: 毎週火曜日 15:00 JST
- **抽出期間**: 前回火曜日 15:00 〜 今回火曜日 14:59（直前7日間）
- **実行方式**: cron または GitHub Actions（後述）

---

## 4. 機能要件

### 4-1. Slackメッセージ取得

- Slack Web API の `conversations.history` エンドポイントを使用
- 取得対象：対象チャンネルの通常メッセージ（ボットメッセージは除外オプションあり）
- スレッドの返信も取得する場合は `conversations.replies` を併用
- 取得フィールド：投稿者名、投稿日時、本文テキスト、リアクション数（任意）

```python
# 取得パラメータ例
params = {
    "channel": CHANNEL_ID,
    "oldest": start_timestamp,  # 前回火曜15:00のUNIX時刻
    "latest": end_timestamp,    # 今回火曜15:00のUNIX時刻
    "limit": 200,               # 1回の取得上限（ページネーション対応）
}
```

### 4-2. メッセージ整形

- タイムスタンプを `YYYY-MM-DD HH:MM` 形式（JST）に変換
- メンションの `<@UXXXXXXX>` をユーザー名に変換（`users.info` API使用）
- 絵文字コード（`:emoji:`）はそのまま or Unicode変換（設定可能）
- 空メッセージ・システムメッセージはスキップ

### 4-3. Confluenceページ出力

- **出力形式**: 毎週の定例ページ（`YYYYMMDD Team B`）の**子ページ**として新規作成
- **親ページの特定方法**: Confluence API で スペース `CD` 内を実行日のYYYYMMDDでタイトル検索し、該当ページのIDを動的に取得する

```python
# 親ページ取得ロジック例
today_str = datetime.now(JST).strftime("%Y%m%d")  # 例: "20260304"
results = confluence.get_all_pages_by_space(
    space="CD",
    start=0, limit=10,
    expand="title"
)
parent_page = next(p for p in results if p["title"].startswith(today_str))
parent_page_id = parent_page["id"]
```

- **子ページタイトル**: `YYYYMMDD 週次Slackレポート`（例：`20260304 週次Slackレポート`）
- **冪等性**: 同タイトルの子ページが既存の場合は上書き更新（重複作成しない）
- **親ページが見つからない場合**: エラーログを出力してスキップ（定例ページ未作成の週に対応）
- **ページ構成**:

```
## 週次Slackレポート - YYYY年MM月DD日

### 📢 全社員向けメッセージ
期間：YYYY-MM-DD 〜 YYYY-MM-DD

#### #all_nippon_mlgr

| 日時 | 投稿者 | メッセージ |
|------|--------|-----------|
| ...  | ...    | ...       |

#### #announcements-all

| 日時 | 投稿者 | メッセージ |
|------|--------|-----------|
| ...  | ...    | ...       |

---

### 👥 AIBAメンバー向けメッセージ
期間：YYYY-MM-DD 〜 YYYY-MM-DD

#### #aiba-all

| 日時 | 投稿者 | メッセージ |
|------|--------|-----------|
| ...  | ...    | ...       |

#### #aiba-edx-all

| 日時 | 投稿者 | メッセージ |
|------|--------|-----------|
| ...  | ...    | ...       |
```

---

## 5. 非機能要件

- **エラーハンドリング**: API失敗時はリトライ（最大3回）し、失敗ログを出力
- **レート制限対応**: Slack APIのTier制限を考慮し、リクエスト間に待機処理を挿入
- **ログ出力**: 実行日時・取得件数・成功/失敗ステータスをログファイルに記録
- **冪等性**: 同じ週に複数回実行しても、重複ページを作成しない（タイトル重複チェック）

---

## 6. 環境変数（`.env`）

```env
# Slack
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx

# Confluence（Atlassian Cloud）
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_USER_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token

# チャンネル設定（全社員向け：2チャンネル）
SLACK_CHANNEL_ID_ALL_NIPPON_MLGR=CGVF155S7         # #all_nippon_mlgr
SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL=C80JUUUMU        # #announcements-all

# チャンネル設定（AIBAメンバー向け：2チャンネル）
SLACK_CHANNEL_ID_AIBA_ALL=C08LJCL2JTG              # #aiba-all
SLACK_CHANNEL_ID_AIBA_EDX_ALL=C0AK24S555F          # #aiba-edx-all

# Confluenceページ設定
CONFLUENCE_SPACE_KEY=CD
# 親ページIDは実行日のYYYYMMDDでタイトル検索して動的取得するため設定不要
```

---

## 7. ディレクトリ構成

```
slack-to-confluence/
├── main.py                  # エントリーポイント（スケジューラから呼び出す）
├── slack_client.py          # Slack APIラッパー
├── confluence_client.py     # Confluence APIラッパー
├── formatter.py             # メッセージ整形ロジック
├── config.py                # 設定・環境変数読み込み
├── requirements.txt         # 依存ライブラリ
├── .env                     # 環境変数（Gitには含めない）
├── .env.example             # 環境変数テンプレート
├── logs/
│   └── app.log              # 実行ログ
└── README.md                # セットアップ手順
```

---

## 8. 依存ライブラリ（requirements.txt）

```
slack-sdk>=3.0.0
atlassian-python-api>=3.0.0
python-dotenv>=1.0.0
pytz>=2024.1
```

---

## 9. スケジューリング設定

### 9-1. cron（サーバー直接実行の場合）

```cron
# 毎週火曜日 15:00 JST（UTC+9 → UTC 06:00）
0 6 * * 2 /usr/bin/python3 /path/to/slack-to-confluence/main.py >> /path/to/logs/cron.log 2>&1
```

### 9-2. GitHub Actions（クラウド実行の場合）

```yaml
# .github/workflows/weekly_report.yml
name: Weekly Slack to Confluence

on:
  schedule:
    - cron: '0 6 * * 2'  # UTC 06:00 = JST 15:00 毎週火曜
  workflow_dispatch:       # 手動実行も可能

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
          CONFLUENCE_BASE_URL: ${{ secrets.CONFLUENCE_BASE_URL }}
          CONFLUENCE_USER_EMAIL: ${{ secrets.CONFLUENCE_USER_EMAIL }}
          CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
          SLACK_CHANNEL_ID_ALL_NIPPON_MLGR: ${{ secrets.SLACK_CHANNEL_ID_ALL_NIPPON_MLGR }}
          SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL: ${{ secrets.SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL }}
          SLACK_CHANNEL_ID_AIBA_ALL: ${{ secrets.SLACK_CHANNEL_ID_AIBA_ALL }}
          SLACK_CHANNEL_ID_AIBA_EDX_ALL: ${{ secrets.SLACK_CHANNEL_ID_AIBA_EDX_ALL }}
          CONFLUENCE_SPACE_KEY_ALL: ${{ secrets.CONFLUENCE_SPACE_KEY_ALL }}
          CONFLUENCE_SPACE_KEY_AIBA: ${{ secrets.CONFLUENCE_SPACE_KEY_AIBA }}
          CONFLUENCE_PARENT_PAGE_ID_ALL: ${{ secrets.CONFLUENCE_PARENT_PAGE_ID_ALL }}
          CONFLUENCE_PARENT_PAGE_ID_AIBA: ${{ secrets.CONFLUENCE_PARENT_PAGE_ID_AIBA }}
```

---

## 10. Slack Bot 権限スコープ（OAuth Scopes）

Bot Token Scopes に以下を追加すること：

| スコープ             | 用途                         |
|----------------------|------------------------------|
| `channels:history`   | パブリックチャンネルの履歴取得 |
| `groups:history`     | プライベートチャンネルの履歴取得 |
| `users:read`         | ユーザー名の解決              |
| `channels:read`      | チャンネル情報の取得          |

---

## 11. 注意事項・TODO

- [ ] 実際のSlackチャンネルID（`CXXXXXXXXX`形式）を環境変数に設定する
- [ ] ConfluenceのスペースキーとページIDを確認して設定する
- [ ] プライベートチャンネルの場合、BotをチャンネルにInviteする必要あり
- [ ] メッセージ数が多い場合はページネーション処理が必要（`cursor`パラメータ使用）
- [ ] 添付ファイル・画像はリンクとして出力する（バイナリ転送は非推奨）