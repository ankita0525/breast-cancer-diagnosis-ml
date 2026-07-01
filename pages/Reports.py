import streamlit as st
import os
from datetime import datetime
from utils.database import (
    get_user_predictions, get_user_reports, save_report, get_user_by_id
)
from utils.pdf_generator import generate_pdf_report

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def show_reports():
    user_id   = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "Patient")

    st.markdown("""
<div class="onco-hero">
    <h1>📄 Diagnostic Reports</h1>
    <p>Generate professional PDF reports for your diagnostic results.</p>
</div>
""", unsafe_allow_html=True)

    # ── Fetch predictions ──────────────────────────────────────────────────
    preds = get_user_predictions(user_id)
    if not preds:
        st.info("🔬 No predictions found. Run a diagnostic analysis first, then return here to generate reports.")
        return

    # ── Choose prediction ──────────────────────────────────────────────────
    st.markdown("#### 🔬 Select Prediction to Report")

    import pandas as pd
    df_pred = pd.DataFrame(preds)
    df_pred["label"] = df_pred.apply(
        lambda r: f"ID #{r['id']} — {r['prediction']} ({r['confidence']:.1f}%) — {r['created_at'][:16]}",
        axis=1
    )
    options = df_pred["label"].tolist()
    selected_label = st.selectbox("Prediction record:", options, key="report_select")

    selected_row = df_pred[df_pred["label"] == selected_label].iloc[0]

    # Preview card
    pred_val  = selected_row["prediction"]
    conf_val  = selected_row["confidence"]
    risk_val  = selected_row["risk_level"]
    pred_id   = int(selected_row["id"])

    col_prev, col_gen = st.columns([1.5, 1])
    with col_prev:
        risk_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(risk_val, "#8b949e")
        diag_color = "#ef4444" if pred_val == "Malignant" else "#22c55e"
        st.markdown(f"""
<div class="onco-card" style="border-left:4px solid {diag_color};">
    <div style="font-size:0.75rem; color:#8b949e; text-transform:uppercase;
                letter-spacing:1px; margin-bottom:6px;">Selected Record</div>
    <div style="display:flex; gap:2rem; align-items:center; flex-wrap:wrap;">
        <div>
            <div class="stat-label">Diagnosis</div>
            <div style="font-size:1.3rem; font-weight:700; color:{diag_color};">{pred_val}</div>
        </div>
        <div>
            <div class="stat-label">Confidence</div>
            <div style="font-size:1.3rem; font-weight:700; color:#e6edf3;">{conf_val:.1f}%</div>
        </div>
        <div>
            <div class="stat-label">Risk Level</div>
            <div style="font-size:1.3rem; font-weight:700; color:{risk_color};">{risk_val}</div>
        </div>
        <div>
            <div class="stat-label">Date</div>
            <div style="font-size:0.9rem; color:#8b949e;">{str(selected_row["created_at"])[:16]}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    with col_gen:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        user_data = get_user_by_id(user_id)
        patient_email = user_data["email"] if user_data else ""

        if st.button("📑 Generate PDF Report", use_container_width=True, key="gen_pdf_btn"):
            with st.spinner("Generating PDF…"):
                import json
                features_raw = selected_row.get("features", None)
                prob_mal = None
                if features_raw:
                    try:
                        from utils.ml_engine import predict
                        features = json.loads(features_raw)
                        result   = predict(features)
                        prob_mal = result["probability_malignant"]
                        prob_ben = result["probability_benign"]
                    except Exception:
                        prob_mal = conf_val if pred_val == "Malignant" else (100 - conf_val)
                        prob_ben = 100 - prob_mal
                else:
                    prob_mal = conf_val if pred_val == "Malignant" else (100 - conf_val)
                    prob_ben = 100 - prob_mal

                fpath = generate_pdf_report(
                    patient_name=user_name,
                    patient_email=patient_email,
                    prediction=pred_val,
                    confidence=conf_val,
                    risk_level=risk_val,
                    prob_malignant=prob_mal,
                    prob_benign=prob_ben,
                    prediction_id=pred_id,
                )
                save_report(user_id, fpath)
                st.session_state["last_pdf_path"] = fpath

            st.success("✅ Report generated!")

    # ── Download button ────────────────────────────────────────────────────
    if "last_pdf_path" in st.session_state:
        fpath = st.session_state["last_pdf_path"]
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=os.path.basename(fpath),
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf_btn"
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Past reports ───────────────────────────────────────────────────────
    st.markdown("#### 📁 Previously Generated Reports")
    reports = get_user_reports(user_id)

    if reports:
        import pandas as pd
        rdf = pd.DataFrame(reports)
        rdf["filename"]   = rdf["report_file"].apply(os.path.basename)
        rdf["created_at"] = rdf["created_at"].apply(lambda x: str(x)[:16])
        rdf = rdf[["id", "created_at", "filename"]].copy()
        rdf.columns = ["#", "Generated At", "File Name"]
        st.dataframe(rdf, use_container_width=True, hide_index=True, height=250)

        # Download any past report
        st.markdown("**Download a past report:**")
        past_options = {
            f"#{r['id']} — {str(r['created_at'])[:16]}": r["report_file"]
            for r in reports if os.path.exists(r["report_file"])
        }
        if past_options:
            chosen = st.selectbox("Select report:", list(past_options.keys()), key="past_rpt_sel")
            if st.button("⬇️ Download Selected", key="dl_past_rpt"):
                fpath = past_options[chosen]
                with open(fpath, "rb") as f:
                    pdf_data = f.read()
                st.download_button(
                    "⬇️ Click to Download",
                    data=pdf_data,
                    file_name=os.path.basename(fpath),
                    mime="application/pdf",
                    key="dl_past_pdf"
                )
    else:
        st.info("No reports generated yet.")
