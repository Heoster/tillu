from datetime import datetime, timedelta, timezone

import jwt
import pytest
from app.config import settings
from app.security.dependencies import get_current_user, require_internal_secret
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_current_user_valid_token(monkeypatch):
    monkeypatch.setattr(settings, "enable_jwt_verification", True)
    test_secret = "test-secret-with-at-least-32-bytes!!"
    monkeypatch.setattr(settings, "secret_key", test_secret)
    monkeypatch.setattr(settings, "single_user_id", "tillu-user")

    token = jwt.encode(
        {
            "sub": "tillu-user",
            "user_id": "tillu-user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        test_secret,
        algorithm="HS256",
    )

    user = await get_current_user(f"Bearer {token}")
    assert user["user_id"] == "tillu-user"


@pytest.mark.asyncio
async def test_get_current_user_rejects_wrong_user(monkeypatch):
    monkeypatch.setattr(settings, "enable_jwt_verification", True)
    test_secret = "test-secret-with-at-least-32-bytes!!"
    monkeypatch.setattr(settings, "secret_key", test_secret)
    monkeypatch.setattr(settings, "single_user_id", "tillu-user")

    token = jwt.encode(
        {
            "sub": "someone-else",
            "user_id": "someone-else",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        test_secret,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        await get_current_user(f"Bearer {token}")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_internal_secret_required(monkeypatch):
    monkeypatch.setattr(settings, "internal_secret", "internal-test-secret")
    monkeypatch.setattr(settings, "single_user_id", "tillu-user")

    internal = await require_internal_secret("internal-test-secret")
    assert internal == {"user_id": "tillu-user", "internal": True}

    with pytest.raises(HTTPException) as exc:
        await require_internal_secret("wrong")
    assert exc.value.status_code == 401
