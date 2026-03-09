"""CLIエントリーポイントのテスト"""
import pytest
from unittest.mock import MagicMock, patch
from propo_suporter.main import PropoSuporter
from propo_suporter.requirement_organizer import OrganizedRequirements
from propo_suporter.proposal_generator import ProposalDraft
from propo_suporter.format_checker import CheckResult, CheckIssue


class TestPropoSuporter:
    """PropoSuporterのエンドツーエンドフローのテスト"""

    @pytest.fixture
    def mock_organizer(self):
        organizer = MagicMock()
        organizer.organize.return_value = OrganizedRequirements(
            background="顧客はシステムリニューアルを検討している",
            issues="現行システムが老朽化している",
            requests="半年以内に刷新したい",
        )
        return organizer

    @pytest.fixture
    def mock_generator(self):
        generator = MagicMock()
        generator.generate.return_value = ProposalDraft(
            proposal_points=["点1", "点2", "点3"],
            development_policy="アジャイル開発で推進する",
        )
        return generator

    @pytest.fixture
    def mock_checker(self):
        checker = MagicMock()
        checker.check.return_value = CheckResult(issues=[], is_ok=True)
        return checker

    @pytest.fixture
    def app(self, mock_organizer, mock_generator, mock_checker):
        return PropoSuporter(
            organizer=mock_organizer,
            generator=mock_generator,
            checker=mock_checker,
        )

    def test_run_returns_result_dict(self, app):
        """run()が結果辞書を返す"""
        result = app.run("ヒアリングメモ")
        assert isinstance(result, dict)

    def test_run_result_has_requirements_key(self, app):
        """結果に'requirements'キーが含まれる"""
        result = app.run("ヒアリングメモ")
        assert "requirements" in result

    def test_run_result_has_proposal_key(self, app):
        """結果に'proposal'キーが含まれる"""
        result = app.run("ヒアリングメモ")
        assert "proposal" in result

    def test_run_result_has_check_key(self, app):
        """結果に'check'キーが含まれる"""
        result = app.run("ヒアリングメモ")
        assert "check" in result

    def test_run_calls_organizer_with_notes(self, app, mock_organizer):
        """organizerにヒアリングメモが渡される"""
        notes = "テスト用ヒアリングメモ"
        app.run(notes)
        mock_organizer.organize.assert_called_once_with(notes)

    def test_run_calls_generator_with_organized_requirements(self, app, mock_organizer, mock_generator):
        """generatorに与件整理結果が渡される"""
        app.run("ヒアリングメモ")
        mock_generator.generate.assert_called_once_with(mock_organizer.organize.return_value)

    def test_run_calls_checker_with_draft_text(self, app, mock_checker):
        """checkerに生成されたドラフトテキストが渡される"""
        app.run("ヒアリングメモ")
        mock_checker.check.assert_called_once()

    def test_run_with_empty_notes_raises_value_error(self, app):
        """空のメモはValueErrorを発生させる"""
        with pytest.raises(ValueError, match="ヒアリングメモが空です"):
            app.run("")

    def test_check_result_is_ok_true_when_no_issues(self, app):
        """チェック結果に問題がなければis_okがTrue"""
        result = app.run("ヒアリングメモ")
        assert result["check"].is_ok is True

    def test_check_result_has_issues_when_problems_found(
        self, mock_organizer, mock_generator
    ):
        """問題がある場合はissuesにCheckIssueが含まれる"""
        checker = MagicMock()
        checker.check.return_value = CheckResult(
            issues=[CheckIssue(category="敬称", description="御社を貴社に変更してください")],
            is_ok=False,
        )
        app = PropoSuporter(
            organizer=mock_organizer,
            generator=mock_generator,
            checker=checker,
        )
        result = app.run("ヒアリングメモ")
        assert result["check"].is_ok is False
        assert len(result["check"].issues) == 1
