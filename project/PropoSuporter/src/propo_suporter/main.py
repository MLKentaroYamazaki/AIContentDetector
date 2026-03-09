"""PropoSuporter CLIエントリーポイント"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

from .requirement_organizer import RequirementOrganizer, OrganizedRequirements, _extract_json
from .proposal_generator import ProposalGenerator, ProposalDraft
from .format_checker import FormatChecker, CheckResult


def _build_llm_client():
    """環境変数 LLM_BACKEND に応じてLLMクライアントを生成する。

    LLM_BACKEND=groq   → Groq API（GROQ_API_KEY が必要）
    LLM_BACKEND=ollama → Ollama ローカル（インストール必要）
    未設定 or anthropic → Anthropic API（ANTHROPIC_API_KEY が必要）
    """
    backend = os.getenv("LLM_BACKEND", "anthropic").lower()

    if backend == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            print("エラー: GROQ_API_KEY が設定されていません。")
            sys.exit(1)
        from .openai_adapter import OpenAICompatibleAdapter
        return OpenAICompatibleAdapter(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

    if backend == "ollama":
        from .openai_adapter import OpenAICompatibleAdapter
        return OpenAICompatibleAdapter(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    # デフォルト: Anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("エラー: ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")
        sys.exit(1)
    from anthropic import Anthropic
    return Anthropic()


class PropoSuporter:
    """与件整理 → 提案骨子生成 → フォーマットチェックを一括実行する"""

    def __init__(
        self,
        organizer: Optional[RequirementOrganizer] = None,
        generator: Optional[ProposalGenerator] = None,
        checker: Optional[FormatChecker] = None,
    ):
        self._organizer = organizer or RequirementOrganizer()
        self._generator = generator or ProposalGenerator()
        self._checker = checker or FormatChecker()

    def run(self, raw_notes: str) -> dict:
        if not raw_notes.strip():
            raise ValueError("ヒアリングメモが空です")

        requirements: OrganizedRequirements = self._organizer.organize(raw_notes)
        proposal: ProposalDraft = self._generator.generate(requirements)

        draft_text = self._build_draft_text(proposal)
        check: CheckResult = self._checker.check(draft_text)

        return {
            "requirements": requirements,
            "proposal": proposal,
            "check": check,
        }

    def _build_draft_text(self, proposal: ProposalDraft) -> str:
        points = "\n".join(f"- {p}" for p in proposal.proposal_points)
        return f"{points}\n{proposal.development_policy}"


def _print_result(result: dict) -> None:
    req = result["requirements"]
    prop = result["proposal"]
    check = result["check"]

    print("\n" + "=" * 60)
    print("【Step 1】与件整理")
    print("=" * 60)
    print(f"背景:\n  {req.background}")
    print(f"課題:\n  {req.issues}")
    print(f"要望:\n  {req.requests}")

    print("\n" + "=" * 60)
    print("【Step 2】提案骨子ドラフト")
    print("=" * 60)
    print("ご提案ポイント:")
    for i, point in enumerate(prop.proposal_points, 1):
        print(f"  {i}. {point}")
    print(f"\n開発方針:\n  {prop.development_policy}")

    print("\n" + "=" * 60)
    print("【Step 3】フォーマット・論理チェック")
    print("=" * 60)
    if check.is_ok:
        print("✅ 問題なし")
    else:
        print(f"⚠️  {len(check.issues)}件の指摘があります:")
        for issue in check.issues:
            print(f"  [{issue.category}] {issue.description}")
    print()


def main() -> None:
    load_dotenv()

    client = _build_llm_client()
    backend = os.getenv("LLM_BACKEND", "anthropic")

    # Groqのデフォルトモデル
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    print(f"バックエンド: {backend}")
    print("ヒアリングメモを入力してください（入力完了後、空行 + Ctrl+D）:")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    raw_notes = "\n".join(lines).strip()
    if not raw_notes:
        print("エラー: ヒアリングメモが空です。")
        sys.exit(1)

    print("\n処理中...")

    # Groq/Ollamaの場合はモデル名を差し替えたオーガナイザー/ジェネレーターを使う
    if backend in ("groq", "ollama"):
        model = groq_model if backend == "groq" else os.getenv("OLLAMA_MODEL", "llama3.2")
        organizer = _make_organizer_with_model(client, model)
        generator = _make_generator_with_model(client, model)
        app = PropoSuporter(organizer=organizer, generator=generator)
    else:
        app = PropoSuporter(
            organizer=RequirementOrganizer(client=client),
            generator=ProposalGenerator(client=client),
        )

    result = app.run(raw_notes)
    _print_result(result)


def _make_organizer_with_model(client, model: str) -> RequirementOrganizer:
    """指定モデルでRequirementOrganizerを生成する"""

    class _CustomOrganizer(RequirementOrganizer):
        def organize(self, raw_notes: str):
            if not raw_notes.strip():
                raise ValueError("ヒアリングメモが空です")
            response = self._client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": (
                        "以下のヒアリングメモから「背景」「課題」「要望」を抽出・整理してください。\n"
                        "必ずJSON形式のみで回答し、他の文章は一切含めないでください。\n\n"
                        "出力形式:\n"
                        '{"background": "...", "issues": "...", "requests": "..."}\n\n'
                        f"ヒアリングメモ:\n{raw_notes}"
                    ),
                }],
            )
            data = _extract_json(response.content[0].text)
            return OrganizedRequirements(**data)

    return _CustomOrganizer(client=client)


def _make_generator_with_model(client, model: str) -> ProposalGenerator:
    """指定モデルでProposalGeneratorを生成する"""

    class _CustomGenerator(ProposalGenerator):
        def generate(self, requirements):
            response = self._client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": (
                        "以下の与件整理情報をもとに、提案書の「ご提案ポイント（3〜4点）」と「開発方針」を作成してください。\n"
                        "必ずJSON形式のみで回答し、他の文章は一切含めないでください。\n\n"
                        "出力形式:\n"
                        '{"proposal_points": ["点1", "点2", "点3"], "development_policy": "..."}\n\n'
                        f"背景: {requirements.background}\n"
                        f"課題: {requirements.issues}\n"
                        f"要望: {requirements.requests}"
                    ),
                }],
            )
            data = _extract_json(response.content[0].text)
            return ProposalDraft(**data)

    return _CustomGenerator(client=client)


if __name__ == "__main__":
    main()
