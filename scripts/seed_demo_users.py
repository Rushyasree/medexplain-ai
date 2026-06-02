from __future__ import annotations

from modules.database import User, init_db, session_scope
from modules.security import hash_password


DEMO_USERS = [
    ("patient_demo", "Patient Demo", "patient", "Patient@123"),
    ("doctor_demo", "Doctor Demo", "doctor", "Doctor@123"),
    ("admin_demo", "Admin Demo", "admin", "Admin@123"),
]


def seed() -> None:
    init_db()
    with session_scope() as session:
        for username, full_name, role, password in DEMO_USERS:
            exists = session.query(User).filter(User.username == username).first()
            if exists:
                continue
            session.add(
                User(
                    username=username,
                    full_name=full_name,
                    role=role,
                    password_hash=hash_password(password),
                    consent_given=1,
                )
            )


if __name__ == "__main__":
    seed()
    print("Demo users ready:")
    for username, _, role, password in DEMO_USERS:
        print(f"- {username} / {password} ({role})")
