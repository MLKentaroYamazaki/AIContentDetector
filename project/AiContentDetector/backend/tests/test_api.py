"""POST /api/v1/analyze エンドポイントの統合テスト"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAnalyzeEndpoint:
    def test_returns_200_with_valid_text(self):
        """正常なテキストを送信すると200を返す"""
        response = client.post("/api/v1/analyze", json={"content": "これはテスト用のテキストです。普通の文章を使います。短い。"})
        assert response.status_code == 200

    def test_response_contains_required_fields(self):
        """レスポンスに必須フィールドが含まれる"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        body = response.json()
        assert "overall_score" in body
        assert "statistical_score" in body
        assert "similarity_score" in body
        assert "breakdown" in body
        assert "highlighted_sections" in body

    def test_overall_score_is_integer_between_0_and_100(self):
        """overall_score は 0〜100 の整数"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        score = response.json()["overall_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_statistical_score_is_integer_between_0_and_100(self):
        """statistical_score は 0〜100 の整数"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        score = response.json()["statistical_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_breakdown_has_sentence_variability(self):
        """breakdown に sentence_variability が含まれる"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        breakdown = response.json()["breakdown"]
        assert "sentence_variability" in breakdown
        assert isinstance(breakdown["sentence_variability"], float)

    def test_breakdown_has_top_k_overlap(self):
        """breakdown に top_k_overlap が含まれる"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。確認用です。"})
        breakdown = response.json()["breakdown"]
        assert "top_k_overlap" in breakdown
        assert isinstance(breakdown["top_k_overlap"], float)

    def test_highlighted_sections_is_list(self):
        """highlighted_sections はリスト"""
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
        response = client.post("/api/v1/analyze", json={"content": ""})
        assert response.status_code == 200
        assert response.json()["overall_score"] == 50

    def test_similarity_score_is_placeholder_until_phase3(self):
        """Phase3実装前は similarity_score は -1（未実装）"""
        response = client.post("/api/v1/analyze", json={"content": "テスト文章です。"})
        assert response.json()["similarity_score"] == -1
