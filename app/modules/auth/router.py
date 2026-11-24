from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.limiter import limiter
from app.core.security import create_access_token, get_current_user, require_admin
from app.db.models import User
from app.db.session import get_db
from .schemas import RegisterRequest, TokenOut, UserOut
from .service import register, authenticate

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_route(body: RegisterRequest, db: Session = Depends(get_db)):
    return register(db, body.email, body.password)

@router.post("/login", response_model=TokenOut)
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form.username, form.password)
    return TokenOut(access_token=create_access_token(user))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.get("/admin", response_model=UserOut)
def admin_only(user: User = Depends(require_admin)):
    return user
