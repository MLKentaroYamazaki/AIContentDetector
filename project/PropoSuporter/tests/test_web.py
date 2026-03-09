"""FastAPI Webエンドポイントのテスト"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from propo_suporter.web import create_app
from propo_suporter.requirement_organizer import OrganizedRequirements
from propo_suporter.proposal_generator import ProposalDraft
from propo_suporter.format_checker import CheckResult, CheckIssue


@pytest.fixture
def mock_app_instance():
    app_instance = MagicMock()
    app_instance.run.return_value = {
        "requirements": OrganizedRequirements(
            background="顧客はシステムリニューアルを検討している",
            issues="現行システムが老朽化している",
            requests="半年以内に刷新したい",
        ),
        "proposal": ProposalDraft(
            proposal_points=["点1：高速化", "点2：モバイル対応", "点3：段階的移行"],
            development_policy="アジャイル開発で推進する",
        ),
        "check": CheckResult(issues=[], is_ok=True),
    }
    return app_instance


@pytest.fixture
def client(mock_app_instance):
    app = create_app(app_instance=mock_app_instance)
    return TestClient(app)


class TestGetIndex:
    """GET / のテスト"""

    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_returns_html(self, client):
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]


class TestPostRun:
    """POST /api/run のテスト"""

    def test_returns_200_with_valid_notes(self, client):
        response = client.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        assert response.status_code == 200

    def test_returns_requirements(self, client):
        response = client.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        data = response.json()
        assert "requirements" in data
        assert "background" in data["requirements"]
        assert "issues" in data["requirements"]
        assert "requests" in data["requirements"]

    def test_returns_proposal(self, client):
        response = client.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        data = response.json()
        assert "proposal" in data
        assert "proposal_points" in data["proposal"]
        assert "development_policy" in data["proposal"]

    def test_returns_check(self, client):
        response = client.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        data = response.json()
        assert "check" in data
        assert "is_ok" in data["check"]
        assert "issues" in data["check"]

    def test_returns_422_with_empty_notes(self, client, mock_app_instance):
        mock_app_instance.run.side_effect = ValueError("ヒアリングメモが空です")
        response = client.post("/api/run", json={"raw_notes": ""})
        assert response.status_code == 422

    def test_returns_400_with_missing_field(self, client):
        response = client.post("/api/run", json={})
        assert response.status_code == 422

    def test_check_is_ok_true_when_no_issues(self, client):
        response = client.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        data = response.json()
        assert data["check"]["is_ok"] is True
        assert data["check"]["issues"] == []

    def test_check_issues_returned_when_problems_found(self, mock_app_instance):
        mock_app_instance.run.return_value = {
            "requirements": OrganizedRequirements(
                background="背景", issues="課題", requests="要望"
            ),
            "proposal": ProposalDraft(
                proposal_points=["点1"], development_policy="方針"
            ),
            "check": CheckResult(
                issues=[CheckIssue(category="敬称", description="御社を貴社に変更")],
                is_ok=False,
            ),
        }
        from propo_suporter.web import create_app
        app = create_app(app_instance=mock_app_instance)
        c = TestClient(app)
        response = c.post("/api/run", json={"raw_notes": "ヒアリングメモ"})
        data = response.json()
        assert data["check"]["is_ok"] is False
        assert len(data["check"]["issues"]) == 1
        assert data["check"]["issues"][0]["category"] == "敬称"
