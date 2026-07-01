import streamlit as st
from utils.auth import register_user


def show_signup():
    st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#0d1117 0%,#161b22 60%,#1a1f2e 100%) !important; }
</style>
""", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.1, 1])
    with col_c:
        st.markdown("""
<div style="text-align:center; margin-bottom:2rem; margin-top:2rem;">
    <div style="font-size:4rem; line-height:1; margin-bottom:0.5rem;">🩺</div>
    <div style="font-size:2.2rem; font-weight:800; letter-spacing:-1px;
                background:linear-gradient(135deg,#6C63FF,#FF6584);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        OncoSight
    </div>
    <div style="color:#8b949e; font-size:0.9rem; margin-top:4px; letter-spacing:0.5px;">
        Create your diagnostic account
    </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="background:rgba(22,27,34,0.95); border:1px solid rgba(255,255,255,0.08);
            border-radius:18px; padding:2.5rem 2rem; margin-bottom:1.2rem;
            box-shadow:0 24px 64px rgba(0,0,0,0.5);">
    <h2 style="margin:0 0 0.3rem 0; font-size:1.45rem; font-weight:700; color:#e6edf3;">
        Create Account
    </h2>
    <p style="color:#8b949e; margin:0 0 1.8rem 0; font-size:0.88rem;">
        Register to access the diagnostic platform
    </p>
</div>
""", unsafe_allow_html=True)

        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input("👤 Full Name", placeholder="Dr. Jane Smith")
            email     = st.text_input("📧 Email Address", placeholder="you@hospital.org")
            password  = st.text_input("🔑 Password", type="password",
                                       placeholder="Min. 6 characters")
            confirm   = st.text_input("🔑 Confirm Password", type="password",
                                       placeholder="Re-enter password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account →", use_container_width=True)

        if submitted:
            with st.spinner("Creating account…"):
                ok, msg = register_user(full_name, email, password, confirm)
            if ok:
                st.success("✅ " + msg)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("❌ " + msg)

        # ── Back to login ──────────────────────────────────────────────────
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("<p style='color:#8b949e; font-size:0.88rem; margin:0;'>Already have an account?</p>",
                        unsafe_allow_html=True)
        with col2:
            if st.button("Sign In", use_container_width=True, key="goto_login"):
                st.session_state.page = "login"
                st.rerun()

        st.markdown("""
<div style="margin-top:1.5rem; text-align:center; font-size:0.75rem; color:#8b949e;">
    By creating an account you agree to use this platform<br>
    for <span style="color:#6C63FF;">educational purposes only</span>.
</div>
""", unsafe_allow_html=True)
