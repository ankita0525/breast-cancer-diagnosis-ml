import streamlit as st
import os
import sys

# ── Page config (MUST be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="OncoSight — Breast Cancer Diagnostic Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "OncoSight v1.0 — Professional Healthcare Diagnostic Platform"
    }
)

# ── Ensure paths are available ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from utils.database import init_db
from utils.styles import inject_global_css

# ── Initialize database ────────────────────────────────────────────────────
init_db()

# ── Inject global CSS ──────────────────────────────────────────────────────
inject_global_css()

# ── Hide Streamlit's default sidebar page navigation ──────────────────────
st.markdown("""
<style>
/* Hide the default Streamlit multipage navigation list */
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Session defaults ───────────────────────────────────────────────────────
for key, default in [
    ("logged_in", False),
    ("user_id",   None),
    ("user_email", None),
    ("user_name", None),
    ("is_admin",  False),
    ("page",      "login"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Route to correct view ──────────────────────────────────────────────────
if not st.session_state.logged_in:
    page = st.session_state.get("page", "login")
    if page == "signup":
        from pages.Signup import show_signup
        show_signup()
    else:
        from pages.Login import show_login
        show_login()
else:
    from utils.sidebar import render_sidebar
    selected = render_sidebar()

    if selected == "Dashboard":
        from pages.Dashboard import show_dashboard
        show_dashboard()
    elif selected == "Prediction":
        from pages.Prediction import show_prediction
        show_prediction()
    elif selected == "History":
        from pages.History import show_history
        show_history()
    elif selected == "Reports":
        from pages.Reports import show_reports
        show_reports()
    elif selected == "Profile":
        from pages.Profile import show_profile
        show_profile()
    elif selected == "Admin Panel":
        from pages.Admin import show_admin
        show_admin()
