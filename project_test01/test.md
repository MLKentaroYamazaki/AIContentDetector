# シンプル TODO アプリ

Next.js と React で構築された高機能なTODOアプリケーション。優先度管理、期限設定、ドラッグ&ドロップによる並び替え機能を備えています。

## 主な機能

### ✅ タスク管理
- タスクの作成、編集、削除
- タスクの完了/未完了の切り替え
- リアルタイムで自動保存（localStorage使用）

### 🎯 優先度管理
- 3段階の優先度設定（高・中・低）
- 優先度ごとの色分け表示
  - **高**: 赤色
  - **中**: 黄色
  - **低**: 青色

### 📅 期限管理
- カレンダーから期限日を設定
- 期限切れタスクの自動検出と警告表示
- 今日が期限のタスクの強調表示

### 🔄 ドラッグ&ドロップ
- タスクの順序をドラッグ&ドロップで簡単に変更
- @dnd-kit/core を使用した滑らかな操作感

### 🔍 フィルタリング
- **すべて**: 全タスクを表示
- **未完了**: 未完了のタスクのみ表示
- **完了済み**: 完了したタスクのみ表示

### 🌓 ダークモード
- ライト/ダークテーマの切り替え
- システム設定との自動同期
- next-themes による実装

## 技術スタック

### フロントエンド
- **Next.js** 14.2.0 - Reactフレームワーク
- **React** 18.2.0 - UIライブラリ
- **TypeScript** 5.0.0 - 型安全性の確保
- **Tailwind CSS** 3.4.0 - スタイリング

### 主要ライブラリ
- **@dnd-kit** - ドラッグ&ドロップ機能
  - @dnd-kit/core ^6.1.0
  - @dnd-kit/sortable ^8.0.0
  - @dnd-kit/utilities ^3.2.2
- **next-themes** ^0.2.1 - テーマ切り替え
- **react-day-picker** ^8.10.0 - 日付選択
- **date-fns** ^2.30.0 - 日付操作
- **nanoid** ^5.0.0 - 一意なID生成

## プロジェクト構造

```
project/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # ルートレイアウト
│   └── page.tsx             # ホームページ
├── components/              # Reactコンポーネント
│   ├── TodoApp.tsx          # メインアプリケーション
│   ├── TodoList.tsx         # タスクリスト
│   ├── TodoItem.tsx         # 個別タスク項目
│   ├── TodoInput.tsx        # タスク入力フォーム
│   ├── TodoFilters.tsx      # フィルター切り替え
│   ├── TodoText.tsx         # タスクテキスト編集
│   ├── PriorityBadge.tsx    # 優先度バッジ
│   ├── PrioritySelector.tsx # 優先度選択
│   ├── DueDateBadge.tsx     # 期限バッジ
│   ├── DatePicker.tsx       # 日付ピッカー
│   ├── EmptyState.tsx       # 空状態の表示
│   └── ThemeToggle.tsx      # テーマ切り替えボタン
├── hooks/                   # カスタムフック
│   ├── useTodos.ts          # タスク管理ロジック
│   └── useLocalStorage.ts   # localStorage連携
├── lib/                     # ユーティリティ
│   ├── constants.ts         # 定数定義
│   ├── migration.ts         # データマイグレーション
│   └── dateHelpers.ts       # 日付ヘルパー関数
├── types/                   # 型定義
│   └── todo.ts              # Todo型定義
└── package.json             # 依存関係管理
```

## データ構造

### Todo型定義 ([types/todo.ts](types/todo.ts))

```typescript
export type TodoPriority = 'high' | 'medium' | 'low';
export type TodoFilter = 'all' | 'active' | 'completed';

export interface Todo {
  id: string;              // 一意な識別子（nanoid）
  text: string;            // タスクのテキスト
  completed: boolean;      // 完了状態
  createdAt: number;       // 作成日時（Unix timestamp）
  updatedAt: number;       // 更新日時（Unix timestamp）
  priority: TodoPriority;  // 優先度
  dueDate: number | null;  // 期限日（Unix timestamp）
  order: number;           // 表示順序
}
```

## セットアップ方法

### 必要要件
- Node.js 18.0以上
- npm または yarn

### インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd project

# 依存関係のインストール
npm install
```

### 開発サーバーの起動

```bash
# 開発モードで起動
npm run dev
```

ブラウザで `http://localhost:3000` を開いてアプリケーションを確認できます。

### ビルド

```bash
# プロダクションビルド
npm run build

# プロダクションサーバーの起動
npm start
```

### リント

```bash
# ESLintでコードチェック
npm run lint
```

## 使い方

### タスクの作成
1. 上部の入力フォームにタスクを入力
2. Enter キーまたは「追加」ボタンをクリック

### 優先度の設定
- タスク作成時または編集時に、ドロップダウンから優先度を選択
- 高（赤）、中（黄）、低（青）から選択可能

### 期限の設定
1. タスク項目のカレンダーアイコンをクリック
2. カレンダーから日付を選択
3. 期限切れのタスクは自動的に警告色で表示

### タスクの並び替え
- タスク項目をドラッグして好きな位置にドロップ
- 順序は自動的に保存される

### タスクの編集
1. タスクのテキスト部分をクリック
2. テキストを編集
3. Enter キーまたは外側をクリックで確定

### タスクの削除
- タスク項目の右側の削除アイコンをクリック

### フィルタリング
- 画面下部のフィルターボタンで表示するタスクを切り替え
  - **すべて**: 全タスク
  - **未完了**: 未完了のみ
  - **完了済み**: 完了済みのみ

### テーマ切り替え
- 右上のテーマ切り替えボタンでライト/ダークモードを切り替え

## データの保存

アプリケーションは `localStorage` を使用してデータを保存します。

- **保存キー**: `todos`
- **自動保存**: タスクの変更時に自動的に保存
- **永続性**: ブラウザを閉じても データは保持されます

## カスタマイズ

### 優先度の色変更

[components/PriorityBadge.tsx](components/PriorityBadge.tsx) で優先度ごとの色を変更できます。

### 日付フォーマットの変更

[lib/dateHelpers.ts](lib/dateHelpers.ts) で日付の表示形式をカスタマイズできます。

### テーマカラーの変更

[app/globals.css](app/globals.css) で Tailwind のテーマ色を変更できます。

## ライセンス

このプロジェクトはプライベートプロジェクトです。

## 今後の拡張案

- [ ] カテゴリー/タグ機能
- [ ] 繰り返しタスク
- [ ] サブタスク機能
- [ ] データのエクスポート/インポート
- [ ] マルチデバイス同期（クラウド保存）
- [ ] タスクの検索機能
- [ ] 統計・分析ダッシュボード

## 改修履歴

### Version 2.1 (最新)
**リリース日**: 2026-01-22

#### useTodos.ts の機能強化

**通知機能の追加**
- `sonner`ライブラリによるトースト通知を統合
- ユーザーフィードバックの改善

**追加された通知**
- タスク追加時: 「タスクを追加しました」
- タスク削除時: 「タスクを削除しました」
- タスク完了/未完了切り替え時: 状態に応じたメッセージ
- エラー発生時: 操作ごとの適切なエラーメッセージ

**エラーハンドリングの強化**
- すべての操作に`try-catch`ブロックを追加
- `loadTodos`: データ読み込みエラーの捕捉
- `addTodo`: タスク追加失敗時の処理
- `updateTodo`: タスク更新失敗時の処理
- `deleteTodo`: タスク削除失敗時の処理
- `toggleTodo`: 状態切り替え失敗時の処理

**実装箇所**
- [hooks/useTodos.ts:5](hooks/useTodos.ts#L5) - toast インポート
- [hooks/useTodos.ts:14-24](hooks/useTodos.ts#L14-L24) - loadTodos エラーハンドリング
- [hooks/useTodos.ts:27-50](hooks/useTodos.ts#L27-L50) - addTodo エラーハンドリング
- [hooks/useTodos.ts:53-69](hooks/useTodos.ts#L53-L69) - updateTodo エラーハンドリング
- [hooks/useTodos.ts:72-85](hooks/useTodos.ts#L72-L85) - deleteTodo エラーハンドリング
- [hooks/useTodos.ts:88-109](hooks/useTodos.ts#L88-L109) - toggleTodo エラーハンドリング

**ユーザビリティの向上**
- 操作結果の即時フィードバック
- エラー発生時の明確なメッセージ表示
- コンソールへのエラーログ出力（デバッグ用）

### Version 2.0
**リリース日**: 2025年初旬

**データモデルの拡張**
- 優先度管理機能（high/medium/low）
- 期限設定機能（Unix timestamp）
- ドラッグ&ドロップ用のorder フィールド
- updatedAt フィールドの追加

**マイグレーション機能**
- バージョン管理システムの導入
- v1からv2への自動マイグレーション
- 既存データの互換性維持

**新機能**
- `updateTodoText`: テキスト更新
- `updateTodoPriority`: 優先度更新
- `updateTodoDueDate`: 期限更新
- `reorderTodos`: ドラッグ&ドロップによる並び替え

**技術的改善**
- TypeScriptによる型安全性の向上
- useCallbackによるパフォーマンス最適化
- localStorageへの自動保存

### Version 1.0
**リリース日**: 2024年

**基本機能**
- シンプルなTODO管理
- タスクの追加、削除、完了/未完了の切り替え
- localStorageでのデータ永続化

**初期データ構造**
- id: タスクID
- text: タスク内容
- completed: 完了状態
- createdAt: 作成日時（オプション）

---

**開発者**: Next.js + React + TypeScript で構築
**バージョン**: 2.1.0
