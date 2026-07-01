import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from utils.ml_engine import predict, get_feature_names
from utils.database import save_prediction

# ── Feature metadata (typical clinical ranges for sliders) ─────────────────
FEATURE_HELP = {
    "radius":             ("Radius", "Mean of distances from center to points on the perimeter", 6.0, 28.0, 14.0),
    "texture":            ("Texture", "Standard deviation of gray-scale values", 9.0, 40.0, 19.0),
    "perimeter":          ("Perimeter", "Perimeter of the cell nucleus", 40.0, 190.0, 92.0),
    "area":               ("Area", "Area of the cell nucleus", 140.0, 2500.0, 655.0),
    "smoothness":         ("Smoothness", "Local variation in radius lengths", 0.05, 0.17, 0.096),
    "compactness":        ("Compactness", "Perimeter² / area - 1.0", 0.01, 0.35, 0.104),
    "concavity":          ("Concavity", "Severity of concave portions of the contour", 0.0, 0.43, 0.089),
    "concave_points":     ("Concave Points", "Number of concave portions of the contour", 0.0, 0.20, 0.048),
    "symmetry":           ("Symmetry", "Symmetry of the nucleus", 0.10, 0.30, 0.181),
    "fractal_dimension":  ("Fractal Dimension", "Coastline approximation - 1", 0.04, 0.10, 0.063),
}


def _get_meta(feat: str):
    """Return (label, help, min, max, default) for a feature."""
    for key, meta in FEATURE_HELP.items():
        if key in feat:
            label = meta[0]
            if "_se" in feat:
                label += " SE"
            elif "_worst" in feat:
                label += " Worst"
            else:
                label += " Mean"
            return label, meta[1], float(meta[2]), float(meta[4])
    # Fallback
    label = feat.replace("_", " ").title()
    return label, "", 0.0, 0.0


def show_prediction():
    st.markdown("""
<div class="onco-hero">
    <h1>🔬 Diagnostic Prediction</h1>
    <p>Enter cell nucleus measurements to classify the breast mass.</p>
</div>
""", unsafe_allow_html=True)

    # ── Load feature names ─────────────────────────────────────────────────
    try:
        feature_names = get_feature_names()
    except FileNotFoundError as e:
        st.error(f"❌ Model files not found: {e}")
        st.info("Please ensure `final_best_model.pkl`, `scaler.pkl`, and `feature_names.pkl` exist.")
        return

    # ── Tips ───────────────────────────────────────────────────────────────
    st.markdown("""
<div class="onco-card" style="border-left:4px solid #6C63FF; margin-bottom:1.5rem;">
    <b style="color:#6C63FF;">💡 How to use:</b>
    <span style="color:#8b949e; font-size:0.9rem;">
      Enter the FNA (Fine Needle Aspirate) measurements from the digitized image.
      All 30 features are organised into Mean, Standard Error, and Worst groups.
      Default values represent the dataset mean — adjust based on lab results.
    </span>
</div>
""", unsafe_allow_html=True)

    # ── Input tabs ─────────────────────────────────────────────────────────
    tab_mean, tab_se, tab_worst = st.tabs(
        ["📊 Mean Features", "📈 Standard Error", "🚩 Worst Features"]
    )

    input_data = {}

    with tab_mean:
        mean_feats = [f for f in feature_names if f.endswith("_mean")]
        cols = st.columns(2)
        for i, feat in enumerate(mean_feats):
            label, help_txt, fmin, fdefault = _get_meta(feat)
            fmax = fdefault * 4 + 0.001
            with cols[i % 2]:
                input_data[feat] = st.number_input(
                    label, min_value=0.0, value=fdefault,
                    format="%.5f", help=help_txt, key=f"inp_{feat}"
                )

    with tab_se:
        se_feats = [f for f in feature_names if f.endswith("_se")]
        cols = st.columns(2)
        for i, feat in enumerate(se_feats):
            label, help_txt, fmin, fdefault = _get_meta(feat)
            fdefault = max(fdefault * 0.07, 0.001)
            with cols[i % 2]:
                input_data[feat] = st.number_input(
                    label, min_value=0.0, value=fdefault,
                    format="%.5f", help=help_txt, key=f"inp_{feat}"
                )

    with tab_worst:
        worst_feats = [f for f in feature_names if f.endswith("_worst")]
        cols = st.columns(2)
        for i, feat in enumerate(worst_feats):
            label, help_txt, fmin, fdefault = _get_meta(feat)
            fdefault = fdefault * 1.4
            with cols[i % 2]:
                input_data[feat] = st.number_input(
                    label, min_value=0.0, value=fdefault,
                    format="%.5f", help=help_txt, key=f"inp_{feat}"
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Predict button ─────────────────────────────────────────────────────
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        run_btn = st.button("🚀 Run Diagnostic Analysis", use_container_width=True,
                            key="predict_btn")

    if run_btn:
        with st.spinner("Running ML analysis…"):
            result = predict(input_data)

        prediction   = result["prediction"]
        confidence   = result["confidence"]
        risk_level   = result["risk_level"]
        prob_mal     = result["probability_malignant"]
        prob_ben     = result["probability_benign"]
        user_id      = st.session_state.get("user_id")

        # Save to DB
        save_prediction(
            user_id, prediction, confidence, risk_level,
            features_json=json.dumps({k: round(v, 5) for k, v in input_data.items()})
        )

        # ── Result display ─────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 📋 Analysis Results")

        r_col1, r_col2, r_col3 = st.columns([1.2, 1, 1])

        with r_col1:
            if prediction == "Malignant":
                st.markdown("""
<div class="onco-card" style="border-left:4px solid #ef4444; text-align:center;">
    <div style="font-size:3rem; margin-bottom:8px;">⚠️</div>
    <div style="font-size:1.5rem; font-weight:800; color:#ef4444;">MALIGNANT</div>
    <div style="color:#8b949e; margin-top:6px; font-size:0.88rem;">
        Cancer tissue detected — clinical review required
    </div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown("""
<div class="onco-card" style="border-left:4px solid #22c55e; text-align:center;">
    <div style="font-size:3rem; margin-bottom:8px;">✅</div>
    <div style="font-size:1.5rem; font-weight:800; color:#22c55e;">BENIGN</div>
    <div style="color:#8b949e; margin-top:6px; font-size:0.88rem;">
        Non-cancerous tissue — continue routine monitoring
    </div>
</div>
""", unsafe_allow_html=True)

        with r_col2:
            # Gauge chart
            gauge_color = "#ef4444" if prediction == "Malignant" else "#22c55e"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob_mal,
                number={"suffix": "%", "font": {"color": "#e6edf3", "size": 26}},
                title={"text": "Malignancy<br>Probability", "font": {"color": "#8b949e", "size": 12}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#8b949e"},
                    "bar":  {"color": gauge_color, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50],   "color": "rgba(34,197,94,0.15)"},
                        {"range": [50, 75],  "color": "rgba(245,158,11,0.15)"},
                        {"range": [75, 100], "color": "rgba(239,68,68,0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": gauge_color, "width": 3},
                        "thickness": 0.75,
                        "value": prob_mal,
                    },
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"),
                height=220,
                margin=dict(t=30, b=0, l=20, r=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        with r_col3:
            risk_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(risk_level, "#8b949e")
            risk_icon  = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(risk_level, "⚪")
            st.markdown(f"""
<div class="onco-card" style="text-align:center;">
    <div class="stat-label">Confidence Score</div>
    <div class="stat-value">{confidence:.1f}%</div>
    <div style="height:10px"></div>
    <div class="stat-label">Risk Level</div>
    <div style="font-size:1.3rem; font-weight:700; color:{risk_color};">
        {risk_icon} {risk_level} Risk
    </div>
    <div style="height:10px"></div>
    <div class="stat-label">Probability Split</div>
    <div style="font-size:0.82rem; color:#8b949e; margin-top:4px;">
        Benign: <b style="color:#22c55e;">{prob_ben:.1f}%</b>
        &nbsp;|&nbsp;
        Malignant: <b style="color:#ef4444;">{prob_mal:.1f}%</b>
    </div>
</div>
""", unsafe_allow_html=True)

        # ── Clinical note ──────────────────────────────────────────────────
        if prediction == "Malignant":
            st.error("⚕️ **Clinical Advisory**: This result suggests malignant tissue. "
                     "Seek immediate oncological evaluation. This is a diagnostic aid — "
                     "not a substitute for professional medical judgment.")
        else:
            st.success("⚕️ **Clinical Note**: The model indicates a benign tumor. "
                       "Continue routine screenings as advised by your healthcare provider.")

        # ── Download report option ─────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📄 Go to the **Reports** page to generate and download a detailed PDF diagnostic report.")
