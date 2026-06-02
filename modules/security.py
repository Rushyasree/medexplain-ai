from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

try:
    import bcrypt
except Exception:
    bcrypt = None

try:
    import jwt
except Exception:
    jwt = None

from modules.config import settings


def hash_password(password: str) -> str:
    if bcrypt:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260000)
    return "pbkdf2_sha256$260000$" + base64.b64encode(salt + digest).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2_sha256$"):
        _, rounds, payload = password_hash.split("$", 2)
        raw = base64.b64decode(payload.encode("ascii"))
        salt, expected = raw[:16], raw[16:]
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds))
        return hmac.compare_digest(digest, expected)
    if not bcrypt:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def create_access_token(user_id: int, role: str, minutes: int = 60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "type": "access",
    }
    if jwt:
        return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = (
        _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        + "."
        + _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    )
    signature = hmac.new(settings.jwt_secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return signing_input + "." + _b64url(signature)


def decode_token(token: str) -> dict:
    if jwt:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    signing_input, signature = token.rsplit(".", 1)
    expected = hmac.new(settings.jwt_secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_decode(signature), expected):
        raise ValueError("Invalid token signature")
    payload = json.loads(_b64url_decode(signing_input.split(".", 1)[1]))
    if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token expired")
    return payload
