import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, LoginRequest, Token, ChangePassword
from app.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_user_by_username,
    create_verification_token, decode_verification_token,
)
from app.core.config import FRONTEND_URL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── helpers ──────────────────────────────────────────────────────
def _send_verification_email(email: str, username: str, token: str) -> None:
    """Send the verification link email. Falls back to logging if SMTP not configured."""
    verify_url = f"{FRONTEND_URL}/verify?token={token}"

    if not SMTP_HOST:
        logger.info(
            "SMTP not configured — verification link for %s: %s", username, verify_url,
        )
        return

    import smtplib
    from email.message import EmailMessage

    plain = (
        f"Hi {username},\n\n"
        f"Welcome to Real-Time Price Tracker!\n\n"
        f"Please verify your email by clicking the link below:\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you did not create this account, ignore this email."
    )

    html = f"""\
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1f2937;margin:0;padding:20px;background:#f9fafb;">
      <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">
        <div style="background:#4f46e5;padding:24px 30px;">
          <h1 style="margin:0;color:#fff;font-size:22px;">📧 Verify Your Email</h1>
        </div>
        <div style="padding:24px 30px;">
          <p>Hi <strong>{username}</strong>,</p>
          <p>Thanks for signing up! Please verify your email address:</p>
          <p style="text-align:center;margin:24px 0;">
            <a href="{verify_url}"
               style="background:#4f46e5;color:#fff;padding:12px 28px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
              Verify Email
            </a>
          </p>
          <p style="font-size:13px;color:#6b7280;">
            This link expires in 24 hours. If you didn't sign up, ignore this email.
          </p>
        </div>
        <div style="background:#f3f4f6;padding:16px 30px;text-align:center;font-size:12px;color:#9ca3af;">
          Real-Time Price Tracker
        </div>
      </div>
    </body>
    </html>"""

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = email
    msg["Subject"] = "Verify your email — Real-Time Price Tracker"
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Verification email sent to %s", email)
    except Exception as exc:
        logger.error("Failed to send verification email to %s: %s", email, exc)


# ── routes ───────────────────────────────────────────────────────

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    # 1) Single DB check for username/email
    existing = (
        db.query(User)
        .filter(or_(User.username == data.username, User.email == data.email))
        .first()
    )
    if existing:
        if existing.username == data.username:
            raise HTTPException(status_code=409, detail="Username already exists")
        raise HTTPException(status_code=409, detail="Email already exists")

    # 2) Hash password safely (avoid 500)
    try:
        hashed = hash_password(data.password)  # bcrypt limit: 72 bytes
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long (bcrypt max is 72 bytes). Use a shorter password.",
        )

    # 3) Create user (email_verified defaults to False)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed,
    )
    db.add(user)

    # 4) Commit safely (handles race conditions)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists")

    db.refresh(user)

    # 5) Send verification email
    token = create_verification_token(user.email)
    _send_verification_email(user.email, user.username, token)

    return user


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify a user's email using the token from the verification link."""
    email = decode_verification_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_verified:
        return {"message": "Email already verified"}

    user.email_verified = True
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(current_user: User = Depends(get_current_user)):
    """Resend the verification email for the currently logged-in user."""
    if current_user.email_verified:
        return {"message": "Email already verified"}

    token = create_verification_token(current_user.email)
    _send_verification_email(current_user.email, current_user.username, token)
    return {"message": "Verification email sent"}


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.username)
    return Token(access_token=token)

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password."""
    # Verify current password
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Prevent reusing the same password
    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Hash and save
    try:
        current_user.hashed_password = hash_password(data.new_password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long (bcrypt max is 72 bytes). Use a shorter password.",
        )

    db.commit()
    logger.info("User %s changed their password", current_user.username)
    return {"message": "Password changed successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete the current user's account and all associated data."""
    if current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin accounts cannot be deleted. Demote yourself first from the admin panel.",
        )
    db.delete(current_user)
    db.commit()
    logger.info("User %s deleted their account", current_user.username)
