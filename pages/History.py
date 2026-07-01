import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.database import get_user_predictions


def show_history():
    user_id = st.session_state.get("user_id")

    st.markdown("""
<div class="onco-hero">
    <h1>🕒 Prediction History</h1>
    <p>Browse, search, and export all your previous diagnostic analyses.</p>
</div>
""", unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    preds = get_user_predictions(user_id)
    if not preds:
        st.info("🔬 No predictions yet. Head to the Prediction page to run your first analysis!")
        return

    df = pd.DataFrame(preds)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df_display = df.copy()

    # ── Filters ────────────────────────────────────────────────────────────
    st.markdown("#### 🔍 Search & Filter")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        search_diag = st.selectbox(
            "Diagnosis",
            ["All", "Benign", "Malignant"],
            key="hist_diag_filter"
        )
    with f_col2:
        search_risk = st.selectbox(
            "Risk Level",
            ["All", "Low", "Medium", "High"],
            key="hist_risk_filter"
        )
    with f_col3:
        date_range = st.date_input(
            "Date Range",
            value=(
                df["created_at"].min().date(),
                df["created_at"].max().date()
            ),
            key="hist_date_filter"
        )

    # Apply filters
    if search_diag != "All":
        df_display = df_display[df_display["prediction"] == search_diag]
    if search_risk != "All":
        df_display = df_display[df_display["risk_level"] == search_risk]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        df_display = df_display[
            (df_display["created_at"].dt.date >= start) &
            (df_display["created_at"].dt.date <= end)
        ]

    st.markdown(f"<div style='color:#8b949e; font-size:0.85rem; margin:0.5rem 0;'>"
                f"Showing <b style='color:#6C63FF;'>{len(df_display)}</b> of "
                f"<b>{len(df)}</b> records</div>", unsafe_allow_html=True)

    # ── Summary cards ──────────────────────────────────────────────────────
    total_f  = len(df_display)
    ben_f    = len(df_display[df_display["prediction"] == "Benign"])
    mal_f    = len(df_display[df_display["prediction"] == "Malignant"])
    avg_conf = df_display["confidence"].mean() if total_f else 0

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Filtered Records", total_f)
    sc2.metric("✅ Benign", ben_f)
    sc3.metric("⚠️ Malignant", mal_f)
    sc4.metric("📊 Avg Confidence", f"{avg_conf:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Table ──────────────────────────────────────────────────────────────
    if total_f:
        display_tbl = df_display[[
            "id", "created_at", "prediction", "confidence", "risk_level"
        ]].copy()
        display_tbl["created_at"] = display_tbl["created_at"].dt.strftime("%Y-%m-%d %H:%M")
        display_tbl["confidence"] = display_tbl["confidence"].apply(lambda x: f"{x:.1f}%")
        display_tbl.columns = ["ID", "Date & Time", "Diagnosis", "Confidence", "Risk Level"]
        display_tbl = display_tbl.sort_values("ID", ascending=False)

        st.dataframe(
            display_tbl,
            use_container_width=True,
            hide_index=True,
            height=400,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Export ─────────────────────────────────────────────────────────
        st.markdown("#### 📥 Export Data")
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            csv_buf = io.StringIO()
            df_display[["id", "created_at", "prediction", "confidence", "risk_level"]].to_csv(
                csv_buf, index=False
            )
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_buf.getvalue(),
                file_name=f"oncosight_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_csv"
            )

        with exp_col2:
            st.info("💡 Go to **Reports** to generate individual PDF reports for specific diagnoses.")
    else:
        st.warning("No records match your current filters.")
