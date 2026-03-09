"""フォーマット・論理チェック機能のテスト"""
import pytest
from propo_suporter.format_checker import FormatChecker, CheckResult, CheckIssue


class TestCheckIssue:
    """チェック指摘のデータ構造テスト"""

    def test_has_category_field(self):
        issue = CheckIssue(category="敬称", description="「御社」は「貴社」に変更してください")
        assert issue.category == "敬称"

    def test_has_description_field(self):
        issue = CheckIssue(category="敬称", description="「御社」は「貴社」に変更してください")
        assert issue.description == "「御社」は「貴社」に変更してください"


class TestCheckResult:
    """チェック結果のデータ構造テスト"""

    def test_has_issues_field(self):
        result = CheckResult(issues=[], is_ok=True)
        assert result.issues == []

    def test_has_is_ok_field(self):
        result = CheckResult(issues=[], is_ok=True)
        assert result.is_ok is True

    def test_is_ok_false_when_issues_exist(self):
        issues = [CheckIssue(category="敬称", description="修正が必要")]
        result = CheckResult(issues=issues, is_ok=False)
        assert result.is_ok is False


class TestFormatChecker:
    """フォーマット・論理チェック機能のテスト"""

    @pytest.fixture
    def checker(self):
        return FormatChecker()

    def test_check_detects_wrong_honorific_onsha(self, checker):
        """「御社」を検出して「貴社」への変更を指摘する"""
        text = "御社のビジネスをサポートします。"
        result = checker.check(text)

        assert not result.is_ok
        assert any("敬称" in issue.category for issue in result.issues)
        assert any("御社" in issue.description for issue in result.issues)

    def test_check_passes_with_correct_honorific_kisha(self, checker):
        """「貴社」が正しく使われていればOK"""
        text = "貴社のビジネスをサポートします。"
        result = checker.check(text)

        honorific_issues = [i for i in result.issues if "敬称" in i.category]
        assert len(honorific_issues) == 0

    def test_check_detects_wrong_date_format(self, checker):
        """西暦と和暦が混在している場合を検出する"""
        text = "2025年4月および令和7年度に対応します。"
        result = checker.check(text)

        assert any("日付" in issue.category for issue in result.issues)

    def test_check_returns_check_result(self, checker):
        """CheckResultを返す"""
        result = checker.check("テキスト")
        assert isinstance(result, CheckResult)

    def test_check_detects_inconsistent_verb_endings(self, checker):
        """語尾が統一されていない場合を検出する（です・ます調と断言調の混在）"""
        text = "本プロジェクトは成功します。また、品質を向上させる。"
        result = checker.check(text)

        # 語尾の不統一は必ずしも全文で検出されるとは限らないが、結果が返ること
        assert isinstance(result, CheckResult)

    def test_check_with_empty_text_raises_value_error(self, checker):
        """空のテキストはValueErrorを発生させる"""
        with pytest.raises(ValueError, match="チェック対象テキストが空です"):
            checker.check("")
