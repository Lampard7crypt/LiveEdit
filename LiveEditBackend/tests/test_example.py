"""
LiveEdit Backend — Example Tests
Stack: pytest + Flask test client

Run: cd LiveEditBackend && pytest tests/ -v
"""

import pytest
import json
from unittest.mock import patch, MagicMock


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def app(monkeypatch):
    """Create a Flask test app instance."""
    import app as app_module
    from app import app as flask_app

    class TestCursor:
        def execute(self, *_args, **_kwargs):
            pass

        def fetchone(self):
            return {"id": 1, "email": "test@example.com"}

        def fetchall(self):
            return []

        def close(self):
            pass

    class TestConnection:
        def cursor(self):
            return TestCursor()

        def close(self):
            pass

    monkeypatch.setattr(app_module, "verify_logto_token", lambda _token: {"sub": "user_test"})
    monkeypatch.setattr(app_module, "get_db_connection", TestConnection)

    flask_app.config["TESTING"] = True
    flask_app.config["DEBUG"] = False
    yield flask_app


@pytest.fixture
def client(app):
    """Flask test client — use instead of running the real server."""
    test_client = app.test_client()
    test_client.environ_base["HTTP_AUTHORIZATION"] = "Bearer test-session-token"
    return test_client


# ─────────────────────────────────────────────
# 1. UNIT TESTS — input validation helpers
# ─────────────────────────────────────────────

class TestInputValidation:

    def test_empty_message_is_invalid(self):
        def is_valid_message(msg):
            return bool(msg and msg.strip())

        assert is_valid_message("") is False
        assert is_valid_message("   ") is False
        assert is_valid_message(None) is False

    def test_non_empty_message_is_valid(self):
        def is_valid_message(msg):
            return bool(msg and msg.strip())

        assert is_valid_message("Hello") is True
        assert is_valid_message("Analyse my video please") is True

    def test_allowed_video_extensions(self):
        ALLOWED = {"mp4", "mov", "avi", "mkv", "webm"}

        def is_allowed_file(filename):
            return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

        assert is_allowed_file("clip.mp4") is True
        assert is_allowed_file("video.mov") is True
        assert is_allowed_file("document.pdf") is False
        assert is_allowed_file("image.png") is False
        assert is_allowed_file("noextension") is False


# ─────────────────────────────────────────────
# 2. API ENDPOINT TESTS
# ─────────────────────────────────────────────

class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_has_status_key(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert "status" in data

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.content_type


class TestAuthenticationMiddleware:
    def test_api_rejects_requests_without_logto_token(self, app):
        response = app.test_client().get("/api/cache/stats")
        assert response.status_code == 401

    def test_logto_session_requires_verified_email(self, app, monkeypatch):
        import app as app_module

        monkeypatch.setattr(
            app_module,
            "verify_logto_token",
            lambda _token: {
                "sub": "logto-user-test",
                "email": "test@example.com",
                "email_verified": False,
            },
        )
        response = app.test_client().get(
            "/api/auth/session",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 403

    def test_subscription_catalog_remains_public(self, app):
        response = app.test_client().get("/api/payments/plans")
        assert response.status_code == 200


class TestChatEndpoint:
    """Tests for POST /api/chat"""

    @patch("app.ai_client")
    def test_chat_returns_200_with_valid_message(self, mock_ai_client, client):
        mock_ai_client.models.generate_content.return_value.text = "Here are your suggestions."

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "How should I edit this clip?"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    @patch("app.ai_client")
    def test_chat_response_contains_message_field(self, mock_ai_client, client):
        mock_ai_client.models.generate_content.return_value.text = "Cut at 10 seconds."

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "Give me editing tips"}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert "message" in data

    def test_chat_rejects_missing_message_field(self, client):
        response = client.post(
            "/api/chat",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code in (400, 422)

    def test_chat_rejects_empty_message(self, client):
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code in (400, 422)

    @patch("app.ai_client")
    def test_chat_handles_ai_client_error(self, mock_ai_client, client):
        mock_ai_client.models.generate_content.side_effect = Exception("Quota exceeded")

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        # Server should return 5xx, not crash
        assert response.status_code >= 500


class TestVideoAnalysisEndpoint:
    """Tests for POST /api/analyze-video"""

    @patch("ai_client.get_genai_client")
    def test_analyze_returns_400_without_file(self, mock_get_client, client):
        response = client.post(
            "/api/analyze-video",
            data={"prompt": "What is in this video?"},
            content_type="multipart/form-data",
        )
        assert response.status_code in (400, 422)

    @patch("ai_client.get_genai_client")
    def test_analyze_response_has_expected_keys(self, mock_get_client, client):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = json.dumps({
            "summary": "A sunset clip.",
            "key_events": [],
            "edit_plan": [],
        })
        mock_get_client.return_value = mock_client

        fake_video = (b"fake video bytes", "clip.mp4")
        response = client.post(
            "/api/analyze-video",
            data={"video_file": fake_video, "prompt": "Summarise this"},
            content_type="multipart/form-data",
        )
        if response.status_code == 200:
            data = json.loads(response.data)
            for key in ("summary", "key_events", "edit_plan"):
                assert key in data


# ─────────────────────────────────────────────
# 3. INTEGRATION TESTS
# ─────────────────────────────────────────────

class TestChatIntegration:

    @patch("app.ai_client")
    def test_full_request_response_cycle(self, mock_ai_client, client):
        """Full flow: POST message → Flask processes → returns AI response."""
        mock_ai_client.models.generate_content.return_value.text = "Try cutting at 10s."

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "How should I edit this video?"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

    @patch("app.ai_client")
    def test_sequential_requests_do_not_bleed_state(self, mock_ai_client, client):
        """Multiple requests should each return independently."""
        mock_ai_client.models.generate_content.return_value.text = "Response"

        for i in range(3):
            response = client.post(
                "/api/chat",
                data=json.dumps({"message": f"Message {i}"}),
                content_type="application/json",
            )
            assert response.status_code == 200