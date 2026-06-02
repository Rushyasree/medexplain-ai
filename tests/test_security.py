from modules.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing_roundtrip():
    password_hash = hash_password("StrongPass123")

    assert password_hash != "StrongPass123"
    assert verify_password("StrongPass123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_jwt_roundtrip():
    token = create_access_token(1, "doctor")
    payload = decode_token(token)

    assert payload["sub"] == "1"
    assert payload["role"] == "doctor"
