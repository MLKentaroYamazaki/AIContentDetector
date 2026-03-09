Project Spec: AI Content Detector Web App
1. Overview
ユーザーが入力したテキストが「人間によって書かれたものか」あるいは「生成AIによって書かれたものか」を、統計的分析とAIによる再生成比較の2軸で判定するWebアプリケーション。

2. Tech Stack
Frontend: Next.js (App Router), Tailwind CSS, Lucide React (Icons), Recharts (Visualizations)

Backend: FastAPI (Python 3.10+)

Analysis Libraries: - NumPy, SciPy (統計計算)

scikit-learn (コサイン類似度計算)

MeCab または Janome (日本語形態素解析 - 文構造分析用)

LLM Integration: Claude API (判定の補助・プロンプト逆算用)

3. Core Features & Logic
A. 統計的アプローチ (Statistical Analysis)
文章の構造的な特徴から「自然なゆらぎ」を測定する。

Burstiness (バースト性): 各文の長さの標準偏差を算出。人間は短い文と長い文を混ぜる傾向があり、AIは一定になりやすい。

Perplexity (予測可能性): 次に来る助詞や単語の組み合わせの「意外性」を擬似的にスコア化。

Punctuation Density: 読点（、）や句点（。）の出現頻度と配置パターンの分析。

B. 類似度比較アプローチ (Similarity Comparison)
AIの特徴的な構成パターンを特定する。

Reverse Prompting: 入力テキストから「この文章を生成するための指示書」をClaudeに推測させる。

Re-generation: 推測された指示書をもとに、Claude自身に同条件で文章を生成させる。

Similarity Score: 入力テキストと再生成テキストをベクトル化し、コサイン類似度を算出。

4. API Endpoints (/api/v1/...)
POST /analyze:

Input: { "content": "string" }

Output:

JSON
{
  "overall_score": 85,
  "statistical_score": 70,
  "similarity_score": 95,
  "breakdown": {
    "sentence_variability": 0.45,
    "top_k_overlap": 0.82
  },
  "highlighted_sections": [
    { "text": "...", "ai_probability": 0.92 }
  ]
}
5. UI/UX Design Requirements
Input: シンプルなテキストエリア（最大5,000文字程度）。

Result Display: - 総合判定を「AI確信度」としてパーセンテージで表示。

統計 vs 類似度の比較レーダーチャート。

判定結果に基づいた「人間らしく修正するためのアドバイス」セクション。

6. Implementation Roadmap
Phase 1: FastAPIによる基本的な統計計算APIの実装。

Phase 2: Next.jsでの入力・結果表示画面の作成。

Phase 3: Claude APIを連携させた類似度比較ロジックの実装。

Phase 4: テキストハイライト機能とアドバイス機能の追加。