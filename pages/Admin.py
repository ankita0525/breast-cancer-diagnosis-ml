import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.database import get_all_users, get_all_predictions, get_stats, delete_user


def show_admin():
    # ── Auth guard ─────────────────────────────────────────────────────────
    if not st.session_state.get("is_admin"):
        st.error("🚫 Access Denied. You must be an administrator to view this page.")
        return

    st.markdown("""
<div class="onco-hero">
    <h1>🛡️ Admin Panel</h1>
    <p>System overview, user management, and analytics dashboard.</p>
</div>
""", unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    stats = get_stats()
    users = get_all_users()
    preds = get_all_predictions()

    # ── System KPIs ────────────────────────────────────────────────────────
    st.markdown("#### 📊 System Statistics")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Total Users",       stats["total_users"])
    k2.metric("🔬 Total Predictions", stats["total_predictions"])
    k3.metric("✅ Benign Results",    stats["benign"])
    k4.metric("⚠️ Malignant Results", stats["malignant"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ─────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("#### 🧬 Global Diagnosis Split")
        if stats["total_predictions"]:
            fig = go.Figure(go.Pie(
                labels=["Benign", "Malignant"],
                values=[stats["benign"], stats["malignant"]],
                hole=0.55,
                marker=dict(colors=["#22c55e", "#ef4444"],
                            line=dict(color="#1f2937", width=3)),
                textinfo="label+percent",
                textfont=dict(size=12, color="#e6edf3"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"), showlegend=False,
                margin=dict(t=10,b=10,l=10,r=10), height=260,
                annotations=[dict(
                    text=f"<b>{stats['total_predictions']}</b><br>Total",
                    x=0.5, y=0.5, font_size=15, font_color="#e6edf3", showarrow=False
                )],
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No prediction data available.")

    with ch2:
        st.markdown("#### 📈 Daily Prediction Volume")
        if preds:
            df_p = pd.DataFrame(preds)
            df_p["created_at"] = pd.to_datetime(df_p["created_at"])
            df_p["date"] = df_p["created_at"].dt.date
            daily = df_p.groupby("date").size().reset_index(name="count")
            fig2 = px.bar(
                daily, x="date", y="count",
                color_discrete_sequence=["#6C63FF"]
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10,b=10,l=10,r=10), height=260,
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No prediction data available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs: Users / Predictions ──────────────────────────────────────────
    tab_users, tab_preds = st.tabs(["👥 User Management", "🔬 All Predictions"])

    with tab_users:
        st.markdown("#### Registered Users")
        if users:
            df_u = pd.DataFrame(users)
            df_u["Role"]       = df_u["is_admin"].apply(lambda x: "🛡️ Admin" if x else "👤 Patient")
            df_u["created_at"] = df_u["created_at"].apply(lambda x: str(x)[:16])
            display_u = df_u[["id", "full_name", "email", "Role", "created_at"]].copy()
            display_u.columns = ["ID", "Name", "Email", "Role", "Joined"]
            st.dataframe(display_u, use_container_width=True, hide_index=True, height=320)

            # Delete user
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚠️ Delete User")
            st.warning("This permanently deletes the user and all their associated data.")
            non_admin = [u for u in users if not u["is_admin"]]
            if non_admin:
                del_options = {f"#{u['id']} — {u['full_name']} ({u['email']})": u["id"]
                               for u in non_admin}
                del_choice = st.selectbox("Select user to delete:", list(del_options.keys()),
                                          key="admin_del_user")
                confirm_del = st.checkbox("I confirm I want to permanently delete this user",
                                          key="admin_del_confirm")
                if st.button("🗑️ Delete User", key="admin_del_btn"):
                    if not confirm_del:
                        st.error("Please confirm deletion by checking the box.")
                    else:
                        uid_to_del = del_options[del_choice]
                        if uid_to_del == st.session_state.get("user_id"):
                            st.error("You cannot delete your own account.")
                        else:
                            delete_user(uid_to_del)
                            st.success(f"✅ User deleted.")
                            st.rerun()
            else:
                st.info("No non-admin users to delete.")
        else:
            st.info("No users found.")

    with tab_preds:
        st.markdown("#### All System Predictions")
        if preds:
            df_ap = pd.DataFrame(preds)
            df_ap["created_at"] = df_ap["created_at"].apply(lambda x: str(x)[:16])
            df_ap["confidence"]  = df_ap["confidence"].apply(lambda x: f"{x:.1f}%")
            display_ap = df_ap[["id","full_name","email","prediction","confidence","risk_level","created_at"]].copy()
            display_ap.columns = ["ID","Patient","Email","Diagnosis","Confidence","Risk","Date"]

            # Search
            search_q = st.text_input("🔍 Search by patient name or email:", key="admin_pred_search")
            if search_q:
                mask = (display_ap["Patient"].str.contains(search_q, case=False, na=False) |
                        display_ap["Email"].str.contains(search_q, case=False, na=False))
                display_ap = display_ap[mask]

            st.dataframe(display_ap, use_container_width=True, hide_index=True, height=400)

            import io
            csv_buf = io.StringIO()
            display_ap.to_csv(csv_buf, index=False)
            st.download_button(
                "⬇️ Export All to CSV",
                data=csv_buf.getvalue(),
                file_name="oncosight_all_predictions.csv",
                mime="text/csv",
                key="admin_csv_dl"
            )
        else:
            st.info("No predictions in the system yet.")
