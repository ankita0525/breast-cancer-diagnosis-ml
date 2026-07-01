import streamlit as st
from utils.auth import login_user


def show_login():
    # ── Full-page layout ───────────────────────────────────────────────────
    st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#0d1117 0%,#161b22 60%,#1a1f2e 100%) !important; }
</style>
""", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.1, 1])
    with col_c:
        # ── Brand ──────────────────────────────────────────────────────────
        st.markdown("""
<div style="text-align:center; margin-bottom:2rem; margin-top:2rem;">
    <div style="font-size:4rem; line-height:1; margin-bottom:0.5rem;">🩺</div>
    <div style="font-size:2.2rem; font-weight:800; letter-spacing:-1px;
                background:linear-gradient(135deg,#6C63FF,#FF6584);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        OncoSight
    </div>
    <div style="color:#8b949e; font-size:0.9rem; margin-top:4px; letter-spacing:0.5px;">
        Professional Breast Cancer Diagnostic Platform
    </div>
</div>
""", unsafe_allow_html=True)

        # ── Card ───────────────────────────────────────────────────────────
        st.markdown("""
<div style="background:rgba(22,27,34,0.95); border:1px solid rgba(255,255,255,0.08);
            border-radius:18px; padding:2.5rem 2rem; margin-bottom:1.2rem;
            box-shadow:0 24px 64px rgba(0,0,0,0.5);">
    <h2 style="margin:0 0 0.3rem 0; font-size:1.45rem; font-weight:700; color:#e6edf3;">
        Welcome Back
    </h2>
    <p style="color:#8b949e; margin:0 0 1.8rem 0; font-size:0.88rem;">
        Sign in to your account to continue
    </p>
</div>
""", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email    = st.text_input("📧 Email Address", placeholder="you@example.com")
            password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            with st.spinner("Authenticating…"):
                ok, msg = login_user(email, password)
            if ok:
                st.success("✅ " + msg)
                st.rerun()
            else:
                st.error("❌ " + msg)

        # ── Sign-up link ───────────────────────────────────────────────────
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("<p style='color:#8b949e; font-size:0.88rem; margin:0;'>Don't have an account?</p>",
                        unsafe_allow_html=True)
        with col2:
            if st.button("Create Account", use_container_width=True, key="goto_signup"):
                st.session_state.page = "signup"
                st.rerun()

        # ── Demo credentials ───────────────────────────────────────────────
        st.markdown("""
<div style="margin-top:1.5rem; background:rgba(108,99,255,0.08);
            border:1px solid rgba(108,99,255,0.2); border-radius:10px;
            padding:0.9rem 1rem; font-size:0.8rem; color:#8b949e;">
    🔑 <b style="color:#6C63FF;">Admin credentials</b><br>
    Email: <code style="color:#e6edf3;">admin@oncosight.ai</code><br>
    Password: <code style="color:#e6edf3;">Admin@123</code>
</div>
""", unsafe_allow_html=True)
