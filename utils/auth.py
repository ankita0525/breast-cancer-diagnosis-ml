import bcrypt
import streamlit as st
from utils.database import get_user_by_email, create_user, get_user_by_id


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_current_user() -> dict | None:
    uid = st.session_state.get("user_id")
    if uid:
        return get_user_by_id(uid)
    return None


def login_user(email: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    if not email or not password:
        return False, "Please fill in all fields."
    user = get_user_by_email(email.strip().lower())
    if not user:
        return False, "No account found with that email."
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password."
    # Set session
    st.session_state.logged_in = True
    st.session_state.user_id   = user["id"]
    st.session_state.user_email = user["email"]
    st.session_state.user_name  = user["full_name"]
    st.session_state.is_admin   = bool(user["is_admin"])
    return True, "Login successful."


def register_user(full_name: str, email: str, password: str, confirm: str) -> tuple[bool, str]:
    if not all([full_name, email, password, confirm]):
        return False, "All fields are required."
    if password != confirm:
        return False, "Passwords do not match."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if get_user_by_email(email.strip().lower()):
        return False, "An account with this email already exists."
    pw_hash = hash_password(password)
    create_user(full_name.strip(), email.strip().lower(), pw_hash)
    return True, "Account created successfully! Please log in."


def logout():
    for key in ["logged_in", "user_id", "user_email", "user_name", "is_admin"]:
        st.session_state.pop(key, None)
    st.session_state.page = "login"
