"""docker compose exec api python -m scripts.create_admin"""
import os
from sqlalchemy import select
from app.core.security import hash_password
from app.db.models import User
from app.db.session import SessionLocal

email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
password = os.environ.get("ADMIN_PASSWORD", "")
if not email or len(password) < 8 or password == "CHANGE_ME_TO_A_STRONG_PASSWORD":
    raise SystemExit("Set ADMIN_EMAIL and a strong ADMIN_PASSWORD in .env")
with SessionLocal() as db:
    obj = db.scalar(select(User).where(User.email == email))
    if obj is None:
        db.add(User(email=email, hashed_password=hash_password(password), role="admin"))
    else:
        obj.role = "admin"
        obj.hashed_password = hash_password(password)
    db.commit()
print(f"Admin ready: {email}")
