# CLAUDE.md

## Conversation Guidelines

- 常に日本語で会話する

## Development Philosophy

### Test-Driven Development (TDD)

- 原則としてテスト駆動開発（TDD）で進める
- 期待される入出力に基づき、まずテストを作成する
- 実装コードは書かず、テストのみを用意する
- テストを実行し、失敗を確認する
- テストが正しいことを確認できた段階でコミットする
- その後、テストをパスさせる実装を進める
- 実装中はテストを変更せず、コードを修正し続ける
- すべてのテストが通過するまで繰り返す

## 最近・直近など、現在日時を取り扱う場合
- 必ず `date` コマンドを使って、現在日時を取得すること

## 脆弱性診断
- /security-review を使用して脆弱性診断を行う
- 高 (High)・中 (Medium) の指摘をすべて修正する

# セキュリティ・デプロイチェックマニュアル（アプリコンテスト用）

> このファイルはClaude Codeが自動的に読み込むプロジェクト設定です。
> 実装・レビュー時に必ず以下のルールを遵守してください。

---

## ⚠️ 絶対ルール（3つ）

### ルール1：Google認証の必須化
- アプリの**最初の画面**にGoogle認証を設置すること
- `@monstar-lab.com` ドメイン**のみ**ログイン許可
- 未認証ユーザーはアプリ画面へ**一切アクセス不可**

**例外（認証不要なケース）：**
- 個人情報を扱わず、ログイン機能も不要な公開ツール
- ユーザーデータの保存・送信がない（DB・API通信なし）
- 完全にクライアントサイドで完結する静的計算ツール等

### ルール2：APIキーは必ず環境変数で管理

```typescript
// ❌ 絶対禁止
const apiKey = "sk-1234567890abcdef";

// ✅ 正しい方法
const apiKey = process.env.API_KEY;
```

- `.env` ファイルは必ず `.gitignore` に含める
- ソースコードへのハードコーディング禁止

### ルール3：脆弱性診断の実施
- `/security-review` を実行する
- **High・Medium の指摘は必ずすべて修正**（ゼロになるまで繰り返す）
- Low は任意対応

---

## 実装リファレンス

### Google認証（Next.js + NextAuth）

**インストール**
```bash
npm install next-auth
```

**`app/api/auth/[...nextauth]/route.ts`**
```typescript
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      const email = user.email;
      if (email && email.endsWith("@monstarlab.com")) {
        return true;
      }
      return false;
    },
  },
});

export { handler as GET, handler as POST };
```

**AuthGuardコンポーネント（保護対象ページに必ずラップ）**
```typescript
"use client";
import { useSession, signIn } from "next-auth/react";
import { useEffect } from "react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "loading") return;
    if (!session) signIn("google");
  }, [session, status]);

  if (status === "loading") return <div>Loading...</div>;
  if (!session) return <div>Redirecting...</div>;

  return <>{children}</>;
}
```

**`.env.local`**
```
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
NEXTAUTH_SECRET=32文字以上のランダム文字列  # openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000
```

### Supabase RLS設定例
```sql
CREATE POLICY "Users can read own data" ON users
  FOR SELECT
  USING (auth.uid() = id);
```

**`.env.local` に追加**
```
NEXT_PUBLIC_SUPABASE_URL=xxxx
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxx
SUPABASE_SERVICE_ROLE_KEY=xxxx  # サーバー側のみ使用
```

---

## デプロイ前チェックリスト

コードを提出・デプロイする前に、以下をすべて確認すること。

- [ ] Google認証が最初の画面にある
- [ ] `@monstarlab.com` のみ許可されている（他ドメインで拒否確認済み）
- [ ] `/security-review` の High・Medium が **0件**
- [ ] APIキーの直書きが **0件**
- [ ] `.env` ファイルが git push されていない
- [ ] Supabase の RLS 警告が **0件**
- [ ] Vercel の環境変数がすべて設定済み
- [ ] Google Cloud Console に本番URLのリダイレクトURIが登録済み

---

## Vercel 環境変数（必須）

| 変数名 | 備考 |
|---|---|
| `GOOGLE_CLIENT_ID` | Google Cloud Consoleから取得 |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Consoleから取得 |
| `NEXTAUTH_SECRET` | `openssl rand -base64 32` で生成 |
| `NEXTAUTH_URL` | 初回デプロイ後に本番URLへ更新 |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase Project Settings > API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Project Settings > API |

---

## トラブルシューティング

| 症状 | 確認箇所 |
|---|---|
| Google認証エラー | Cloud ConsoleのリダイレクトURIとVercel環境変数が一致しているか |
| ドメイン制限が効かない | `signIn` コールバックの `endsWith("@monstarlab.com")` を確認 |
| Supabase接続不可 | URL・キーの誤り、RLSポリシーの設定を確認 |
| Vercelビルド失敗 | ローカルで `npm run build` を実行、環境変数不足を確認 |
| `/security-review` が改善しない | 修正が保存・適用されているか再確認 |
