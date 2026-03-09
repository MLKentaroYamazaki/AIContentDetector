"""POST /api/v1/analyze エンドポイントの統合テスト"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Claude APIを使う関数をモック化
MOCK_SIMILARITY_SCORE = 72
MOCK_ADVICE = "文の長さにバラつきを持たせましょう。"


from contextlib import contextmanager

@contextmanager
def _make_client(similarity_score: int = MOCK_SIMILARITY_SCORE, advice: str = MOCK_ADVICE):
    """similarity_score と generate_advice をモックした状態でリクエストを送る"""
    with patch(
        "app.api.v1.endpoints.analyze.calculate_similarity_score",
        new=AsyncMock(return_value=similarity_score),
    ), patch(
        "app.api.v1.endpoints.analyze.generate_advice",
        new=AsyncMock(return_value=advice),
    ):
        yield


class TestAnalyzeEndpoint:
    def test_returns_200_with_valid_text(self):
        """正常なテキストを送信すると200を返す"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "これはテスト用のテキストです。普通の文章を使います。短い。"})
        assert response.status_code == 200

    def test_response_contains_required_fields(self):
        """レスポンスに必須フィールドが含まれる"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        body = response.json()
        assert "overall_score" in body
        assert "statistical_score" in body
        assert "similarity_score" in body
        assert "breakdown" in body
        assert "highlighted_sections" in body

    def test_overall_score_is_integer_between_0_and_100(self):
        """overall_score は 0〜100 の整数"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        score = response.json()["overall_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_statistical_score_is_integer_between_0_and_100(self):
        """statistical_score は 0〜100 の整数"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        score = response.json()["statistical_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_breakdown_has_sentence_variability(self):
        """breakdown に sentence_variability が含まれる"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        breakdown = response.json()["breakdown"]
        assert "sentence_variability" in breakdown
        assert isinstance(breakdown["sentence_variability"], float)

    def test_breakdown_has_top_k_overlap(self):
        """breakdown に top_k_overlap が含まれる"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        breakdown = response.json()["breakdown"]
        assert "top_k_overlap" in breakdown
        assert isinstance(breakdown["top_k_overlap"], float)

    def test_highlighted_sections_is_list(self):
        """highlighted_sections はリスト"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        sections = response.json()["highlighted_sections"]
        assert isinstance(sections, list)

    def test_returns_422_when_content_is_missing(self):
        """content フィールドがない場合は422を返す"""
        response = client.post("/api/v1/analyze", json={})
        assert response.status_code == 422

    def test_returns_422_when_body_is_empty(self):
        """ボディが空の場合は422を返す"""
        response = client.post("/api/v1/analyze")
        assert response.status_code == 422

    def test_empty_content_returns_200(self):
        """空文字は200を返す（判定不能として中間値）"""
        with _make_client(similarity_score=50):
            response = client.post("/api/v1/analyze", json={"content": ""})
        assert response.status_code == 200
        assert response.json()["overall_score"] == 50

    def test_similarity_score_is_integer_between_0_and_100(self):
        """similarity_score は 0〜100 の整数"""
        with _make_client():
            response = client.post("/api/v1/analyze", json={"content": "テスト文章です。"})
        score = response.json()["similarity_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100
