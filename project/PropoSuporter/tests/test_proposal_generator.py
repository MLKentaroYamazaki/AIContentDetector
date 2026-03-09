"""提案骨子作成機能のテスト"""
import pytest
from unittest.mock import MagicMock
from propo_suporter.proposal_generator import ProposalGenerator, ProposalDraft
from propo_suporter.requirement_organizer import OrganizedRequirements


class TestProposalDraft:
    """提案ドラフトのデータ構造テスト"""

    def test_has_proposal_points_field(self):
        draft = ProposalDraft(
            proposal_points=["強み1", "強み2", "強み3"],
            development_policy="アジャイル開発で推進する",
        )
        assert draft.proposal_points == ["強み1", "強み2", "強み3"]

    def test_has_development_policy_field(self):
        draft = ProposalDraft(
            proposal_points=["強み1"],
            development_policy="開発方針テキスト",
        )
        assert draft.development_policy == "開発方針テキスト"

    def test_proposal_points_is_list(self):
        draft = ProposalDraft(
            proposal_points=["点1", "点2"],
            development_policy="方針",
        )
        assert isinstance(draft.proposal_points, list)


class TestProposalGenerator:
    """提案骨子作成機能のテスト"""

    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def generator(self, mock_client):
        return ProposalGenerator(client=mock_client)

    @pytest.fixture
    def sample_requirements(self):
        return OrganizedRequirements(
            background="顧客はECサイトのリニューアルを検討している",
            issues="現行サイトは表示速度が遅く、スマートフォン対応が不十分",
            requests="半年以内にリニューアルを完了したい",
        )

    def test_generate_returns_proposal_draft(self, generator, mock_client, sample_requirements):
        """OrganizedRequirementsからProposalDraftを返す"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "proposal_points": [
                "高速化対応：最新技術でページ速度を3倍に改善",
                "モバイルファースト設計：スマートフォン体験を最優先",
                "段階的移行：リスクを最小化した移行計画"
            ],
            "development_policy": "アジャイル開発で2週間スプリントを基本に推進する"
        }"""
        mock_client.messages.create.return_value = mock_response

        result = generator.generate(sample_requirements)

        assert isinstance(result, ProposalDraft)
        assert isinstance(result.proposal_points, list)
        assert result.development_policy != ""

    def test_generate_proposal_points_count_is_3_to_4(self, generator, mock_client, sample_requirements):
        """提案ポイントは3〜4点であること"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "proposal_points": ["点1", "点2", "点3"],
            "development_policy": "方針"
        }"""
        mock_client.messages.create.return_value = mock_response

        result = generator.generate(sample_requirements)

        assert 3 <= len(result.proposal_points) <= 4

    def test_generate_calls_claude_api(self, generator, mock_client, sample_requirements):
        """Claude APIを呼び出すことを確認"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "proposal_points": ["点1", "点2", "点3"],
            "development_policy": "方針"
        }"""
        mock_client.messages.create.return_value = mock_response

        generator.generate(sample_requirements)

        mock_client.messages.create.assert_called_once()

    def test_generate_includes_requirements_in_prompt(self, generator, mock_client, sample_requirements):
        """与件情報がAPIプロンプトに含まれることを確認"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "proposal_points": ["点1", "点2", "点3"],
            "development_policy": "方針"
        }"""
        mock_client.messages.create.return_value = mock_response

        generator.generate(sample_requirements)

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        prompt_text = str(messages)
        assert sample_requirements.background in prompt_text
