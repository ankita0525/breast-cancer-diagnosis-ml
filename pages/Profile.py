import streamlit as st
import os
from PIL import Image
from utils.database import (
    get_user_by_id, update_user_profile, update_user_password,
    update_profile_image
)
from utils.auth import verify_password, hash_password

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def show_profile():
    user_id = st.session_state.get("user_id")
    user    = get_user_by_id(user_id)

    st.markdown("""
<div class="onco-hero">
    <h1>👤 My Profile</h1>
    <p>Manage your account information and security settings.</p>
</div>
""", unsafe_allow_html=True)

    if not user:
        st.error("User not found.")
        return

    tab_info, tab_avatar, tab_pwd = st.tabs(
        ["📋 Account Info", "🖼️ Profile Picture", "🔑 Change Password"]
    )

    # ── Tab 1: Account info ────────────────────────────────────────────────
    with tab_info:
        col_av, col_form = st.columns([1, 2])

        with col_av:
            avatar_path = user.get("profile_image")
            if avatar_path and os.path.exists(avatar_path):
                img = Image.open(avatar_path)
                st.image(img, width=180)
            else:
                initials = "".join([w[0].upper() for w in user["full_name"].split()[:2]])
                st.markdown(f"""
<div style="width:130px; height:130px; border-radius:50%;
            background:linear-gradient(135deg,#6C63FF,#FF6584);
            display:flex; align-items:center; justify-content:center;
            font-size:2.5rem; font-weight:700; color:#fff; margin:0 auto;">
    {initials}
</div>
""", unsafe_allow_html=True)
            st.markdown(f"""
<div style="text-align:center; margin-top:0.8rem;">
    <div style="font-weight:600; font-size:1rem; color:#e6edf3;">{user['full_name']}</div>
    <div style="font-size:0.8rem; color:#8b949e;">{user['email']}</div>
    <div style="margin-top:0.4rem;">
        {"<span class='badge-malignant'>🛡️ Admin</span>" if user.get('is_admin') else
         "<span class='badge-benign'>👤 Patient</span>"}
    </div>
    <div style="font-size:0.75rem; color:#8b949e; margin-top:0.6rem;">
        Member since {str(user['created_at'])[:10]}
    </div>
</div>
""", unsafe_allow_html=True)

        with col_form:
            st.markdown("#### Edit Profile Information")
            with st.form("profile_form"):
                new_name  = st.text_input("Full Name", value=user["full_name"])
                new_email = st.text_input("Email Address", value=user["email"])
                save_btn  = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if save_btn:
                if not new_name or not new_email:
                    st.error("Name and email cannot be empty.")
                else:
                    update_user_profile(user_id, new_name.strip(), new_email.strip().lower())
                    st.session_state.user_name  = new_name.strip()
                    st.session_state.user_email = new_email.strip().lower()
                    st.success("✅ Profile updated successfully!")
                    st.rerun()

        # Account details card
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Account Details")
        detail_data = {
            "User ID":      user["id"],
            "Full Name":    user["full_name"],
            "Email":        user["email"],
            "Role":         "Administrator" if user.get("is_admin") else "Patient",
            "Joined":       str(user["created_at"])[:19],
        }
        col1, col2 = st.columns(2)
        items = list(detail_data.items())
        for i, (k, v) in enumerate(items):
            with (col1 if i % 2 == 0 else col2):
                st.markdown(f"""
<div class="onco-card" style="padding:0.9rem 1rem; margin-bottom:0.6rem;">
    <div class="stat-label">{k}</div>
    <div style="font-size:0.98rem; font-weight:600; color:#e6edf3; margin-top:2px;">{v}</div>
</div>
""", unsafe_allow_html=True)

    # ── Tab 2: Avatar upload ───────────────────────────────────────────────
    with tab_avatar:
        st.markdown("#### Upload Profile Picture")
        st.info("Supported formats: JPG, JPEG, PNG — Max size: 5 MB")

        uploaded = st.file_uploader(
            "Choose image", type=["jpg", "jpeg", "png"],
            key="avatar_upload", label_visibility="collapsed"
        )
        if uploaded:
            # Validate size
            if uploaded.size > 5 * 1024 * 1024:
                st.error("❌ File too large. Maximum 5 MB allowed.")
            else:
                img = Image.open(uploaded)
                # Preview
                col_p, _ = st.columns([1, 2])
                with col_p:
                    st.image(img, caption="Preview", width=200)

                if st.button("💾 Save Profile Picture", key="save_avatar"):
                    # Save file
                    ext      = uploaded.name.rsplit(".", 1)[-1].lower()
                    filename = f"avatar_{user_id}.{ext}"
                    save_path = os.path.join(UPLOADS_DIR, filename)
                    img.save(save_path)
                    update_profile_image(user_id, save_path)
                    st.success("✅ Profile picture updated!")
                    st.rerun()

    # ── Tab 3: Change password ─────────────────────────────────────────────
    with tab_pwd:
        st.markdown("#### Change Password")
        with st.form("pwd_form"):
            current_pwd = st.text_input("Current Password", type="password", placeholder="••••••••")
            new_pwd     = st.text_input("New Password", type="password",
                                         placeholder="Minimum 6 characters")
            confirm_pwd = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
            save_pwd    = st.form_submit_button("🔑 Update Password", use_container_width=True)

        if save_pwd:
            if not current_pwd or not new_pwd or not confirm_pwd:
                st.error("Please fill in all fields.")
            elif not verify_password(current_pwd, user["password_hash"]):
                st.error("❌ Current password is incorrect.")
            elif new_pwd != confirm_pwd:
                st.error("❌ New passwords do not match.")
            elif len(new_pwd) < 6:
                st.error("❌ Password must be at least 6 characters.")
            else:
                new_hash = hash_password(new_pwd)
                update_user_password(user_id, new_hash)
                st.success("✅ Password updated successfully!")
