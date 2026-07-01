import streamlit as st
from streamlit_option_menu import option_menu
from utils.auth import logout


def render_sidebar() -> str:
    """Renders the sidebar navigation and returns the selected page name."""
    is_admin = st.session_state.get("is_admin", False)
    user_name = st.session_state.get("user_name", "User")

    with st.sidebar:
        # ── Logo & Brand ───────────────────────────────────────────────────
        st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
    <div style="font-size:2.5rem; line-height:1;">🩺</div>
    <div style="font-size:1.35rem; font-weight:800; letter-spacing:-0.5px;
                background:linear-gradient(135deg,#6C63FF,#FF6584);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        OncoSight
    </div>
    <div style="font-size:0.7rem; color:#8b949e; letter-spacing:1.5px;
                text-transform:uppercase; margin-top:2px;">
        Diagnostic Platform
    </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<hr style='margin:0.8rem 0; border-color:rgba(255,255,255,0.08);'>",
                    unsafe_allow_html=True)

        # ── User Badge ─────────────────────────────────────────────────────
        st.markdown(f"""
<div style="display:flex; align-items:center; gap:0.7rem;
            background:rgba(108,99,255,0.1); border:1px solid rgba(108,99,255,0.25);
            border-radius:12px; padding:0.65rem 0.9rem; margin-bottom:0.8rem;">
    <div style="width:36px; height:36px; border-radius:50%;
                background:linear-gradient(135deg,#6C63FF,#FF6584);
                display:flex; align-items:center; justify-content:center;
                font-weight:700; color:#fff; flex-shrink:0;">
        {user_name[0].upper()}
    </div>
    <div>
        <div style="font-weight:600; font-size:0.88rem; color:#e6edf3;">{user_name}</div>
        <div style="font-size:0.7rem; color:#8b949e;">
            {"🛡️ Administrator" if is_admin else "👤 Patient"}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────────────────────
        nav_items  = ["Dashboard", "Prediction", "History", "Reports", "Profile"]
        nav_icons  = ["house-fill", "activity", "clock-history", "file-earmark-text", "person-circle"]

        if is_admin:
            nav_items.append("Admin Panel")
            nav_icons.append("shield-lock-fill")

        selected = option_menu(
            menu_title=None,
            options=nav_items,
            icons=nav_icons,
            default_index=0,
            styles={
                "container":     {"padding": "0", "background": "transparent"},
                "icon":          {"color": "#8b949e", "font-size": "15px"},
                "nav-link":      {
                    "font-size": "0.88rem",
                    "font-weight": "500",
                    "color": "#8b949e",
                    "border-radius": "10px",
                    "padding": "0.6rem 1rem",
                    "margin-bottom": "2px",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #6C63FF, #574fd6)",
                    "color": "#fff",
                    "font-weight": "600",
                },
            },
        )

        # ── Logout ─────────────────────────────────────────────────────────
        st.markdown("<hr style='margin:0.8rem 0; border-color:rgba(255,255,255,0.08);'>",
                    unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_logout"):
            logout()
            st.rerun()

        st.markdown("""
<div style="text-align:center; font-size:0.68rem; color:#8b949e; margin-top:1rem;">
    OncoSight v1.0 &nbsp;|&nbsp; © 2025<br>
    <span style="color:#6C63FF;">For educational use only</span>
</div>
""", unsafe_allow_html=True)

    return selected
