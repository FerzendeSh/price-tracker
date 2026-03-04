"""Admin-only routes for managing users and system configuration."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.deps import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.schemas.user import AdminUserRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Admin guard ──────────────────────────────────────────────────
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# ── Users management ─────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """List all users with product counts."""
    # Exclude admin users — admin manages regular users only
    users = db.query(User).filter(User.is_admin == False).order_by(User.id).all()
    result = []
    for u in users:
        product_count = db.query(func.count(Product.id)).filter(Product.user_id == u.id).scalar()
        result.append(
            AdminUserRead(
                id=u.id,
                username=u.username,
                email=u.email,
                email_verified=u.email_verified,
                is_admin=u.is_admin,
                product_count=product_count,
            )
        )
    return result


@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """System-wide statistics for the admin dashboard."""
    # Exclude admin users from stats
    total_users = db.query(func.count(User.id)).filter(User.is_admin == False).scalar()
    verified_users = db.query(func.count(User.id)).filter(User.is_admin == False, User.email_verified == True).scalar()
    total_products = db.query(func.count(Product.id)).scalar()

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "unverified_users": total_users - verified_users,
        "total_products": total_products,
    }


@router.patch("/users/{user_id}/toggle-admin")
def toggle_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Promote or demote a user as admin."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")

    target.is_admin = not target.is_admin
    db.commit()
    action = "promoted to admin" if target.is_admin else "removed from admin"
    logger.info("User %s %s by admin %s", target.username, action, admin.username)
    return {"message": f"{target.username} {action}", "is_admin": target.is_admin}


@router.patch("/users/{user_id}/verify")
def admin_verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Manually verify a user's email."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.email_verified:
        return {"message": "Already verified"}

    target.email_verified = True
    db.commit()
    logger.info("User %s email verified by admin %s", target.username, admin.username)
    return {"message": f"{target.username} email verified"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Delete a user and all their products/data (admin action)."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account from admin panel")

    username = target.username
    db.delete(target)
    db.commit()
    logger.info("User %s deleted by admin %s", username, admin.username)
