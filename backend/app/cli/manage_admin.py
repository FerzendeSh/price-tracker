#!/usr/bin/env python3
"""
CLI utility to manage admin users.

Usage (from backend/ directory):
    conda run -n FA_project python -m app.cli.manage_admin promote <username>
    conda run -n FA_project python -m app.cli.manage_admin demote  <username>
    conda run -n FA_project python -m app.cli.manage_admin list
"""
import sys
import app.db.models  # noqa: F401 — register all models (User, Product, PriceHistory)
from app.db.session import SessionLocal
from app.models.user import User


def get_db():
    return SessionLocal()


def list_admins():
    db = get_db()
    admins = db.query(User).filter(User.is_admin == True).all()
    if not admins:
        print("No admin users found.")
    else:
        print(f"{'ID':<6} {'Username':<20} {'Email':<35} {'Verified'}")
        print("-" * 70)
        for u in admins:
            print(f"{u.id:<6} {u.username:<20} {u.email:<35} {'Yes' if u.email_verified else 'No'}")
    db.close()


def promote(username: str):
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        sys.exit(1)
    if user.is_admin:
        print(f"'{username}' is already an admin.")
    else:
        user.is_admin = True
        db.commit()
        print(f"✅ '{username}' promoted to admin.")
    db.close()


def demote(username: str):
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        sys.exit(1)
    if not user.is_admin:
        print(f"'{username}' is not an admin.")
    else:
        user.is_admin = False
        db.commit()
        print(f"✅ '{username}' demoted from admin.")
    db.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "list":
        list_admins()
    elif command == "promote":
        if len(sys.argv) < 3:
            print("Usage: manage_admin promote <username>")
            sys.exit(1)
        promote(sys.argv[2])
    elif command == "demote":
        if len(sys.argv) < 3:
            print("Usage: manage_admin demote <username>")
            sys.exit(1)
        demote(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, promote, demote")
        sys.exit(1)


if __name__ == "__main__":
    main()
