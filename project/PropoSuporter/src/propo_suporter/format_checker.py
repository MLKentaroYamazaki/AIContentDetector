"""フォーマット・論理チェック機能"""
import re
from dataclasses import dataclass, field


@dataclass
class CheckIssue:
    category: str
    description: str


@dataclass
class CheckResult:
    issues: list[CheckIssue]
    is_ok: bool


class FormatChecker:
    """敬称・語尾・日付・論理整合性を自動校閲する"""

    # 誤った敬称パターン
    _WRONG_HONORIFICS = ["御社", "貴殿", "御行", "御校"]

    def check(self, text: str) -> CheckResult:
        if not text.strip():
            raise ValueError("チェック対象テキストが空です")

        issues: list[CheckIssue] = []
        issues.extend(self._check_honorifics(text))
        issues.extend(self._check_date_format(text))
        issues.extend(self._check_verb_endings(text))

        return CheckResult(issues=issues, is_ok=len(issues) == 0)

    def _check_honorifics(self, text: str) -> list[CheckIssue]:
        issues = []
        for wrong in self._WRONG_HONORIFICS:
            if wrong in text:
                issues.append(CheckIssue(
                    category="敬称",
                    description=f"「{wrong}」が使われています。「貴社」に統一してください。",
                ))
        return issues

    def _check_date_format(self, text: str) -> list[CheckIssue]:
        issues = []
        has_western = bool(re.search(r"\d{4}年", text))
        has_japanese_era = bool(re.search(r"(令和|平成|昭和)\d+年", text))

        if has_western and has_japanese_era:
            issues.append(CheckIssue(
                category="日付",
                description="西暦と和暦が混在しています。どちらかに統一してください。",
            ))
        return issues

    def _check_verb_endings(self, text: str) -> list[CheckIssue]:
        issues = []
        has_keigo = bool(re.search(r"(します|ます|です|ください|ありません)。", text))
        # 「します。」「できます。」「あります。」などの敬体を除外した常体パターン
        jotai_patterns = [r"[^すまでき]する。", r"できる。", r"[^あ]ある。", r"いる。", r"よい。"]
        has_jotai = any(re.search(p, text) for p in jotai_patterns)

        if has_keigo and has_jotai:
            issues.append(CheckIssue(
                category="語尾",
                description="「です・ます」調と常体（「〜する」「〜ある」）が混在しています。「です・ます」調に統一してください。",
            ))
        return issues
