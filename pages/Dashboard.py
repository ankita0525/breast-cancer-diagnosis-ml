import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.database import get_user_predictions, get_stats


def show_dashboard():
    user_name = st.session_state.get("user_name", "User")
    user_id   = st.session_state.get("user_id")

    # ── Hero ───────────────────────────────────────────────────────────────
    now   = datetime.now()
    hour  = now.hour
    greet = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"

    st.markdown(f"""
<div class="onco-hero">
    <div style="font-size:0.9rem; color:rgba(255,255,255,0.75); letter-spacing:1px;
                text-transform:uppercase; margin-bottom:4px;">
        {now.strftime("%A, %B %d, %Y")}
    </div>
    <h1>
        {greet}, {user_name.split()[0]} 👋
    </h1>
    <p>Welcome to your OncoSight diagnostic dashboard.</p>
</div>
""", unsafe_allow_html=True)

    # ── Fetch data ─────────────────────────────────────────────────────────
    preds = get_user_predictions(user_id)
    df    = pd.DataFrame(preds) if preds else pd.DataFrame()

    total     = len(df)
    malignant = len(df[df["prediction"] == "Malignant"]) if total else 0
    benign    = total - malignant
    high_risk = len(df[df["risk_level"] == "High"]) if total else 0

    # ── KPI cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🔬 Total Analyses", total, help="All-time predictions run by you")
    with c2:
        st.metric("✅ Benign Results", benign,
                  delta=f"{(benign/total*100):.0f}% of total" if total else None)
    with c3:
        st.metric("⚠️ Malignant Results", malignant,
                  delta=f"{(malignant/total*100):.0f}% of total" if total else None,
                  delta_color="inverse")
    with c4:
        st.metric("🔴 High Risk Cases", high_risk)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1, 1.5])

    with col_a:
        st.markdown("#### 🧬 Diagnosis Distribution")
        if total:
            fig_pie = go.Figure(go.Pie(
                labels=["Benign", "Malignant"],
                values=[benign, malignant],
                hole=0.55,
                marker=dict(colors=["#22c55e", "#ef4444"],
                            line=dict(color="#1f2937", width=3)),
                textinfo="label+percent",
                textfont=dict(size=12, color="#e6edf3"),
            ))
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"),
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
                annotations=[dict(
                    text=f"<b>{total}</b><br>Cases",
                    x=0.5, y=0.5, font_size=16,
                    font_color="#e6edf3", showarrow=False
                )],
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No predictions yet. Run your first analysis!")

    with col_b:
        st.markdown("#### 📈 Prediction Trend (Last 30 Days)")
        if total and "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df_30 = df[df["created_at"] >= datetime.now() - timedelta(days=30)].copy()
            df_30["date"] = df_30["created_at"].dt.date
            daily = df_30.groupby(["date", "prediction"]).size().reset_index(name="count")

            fig_line = px.line(
                daily, x="date", y="count", color="prediction",
                color_discrete_map={"Benign": "#22c55e", "Malignant": "#ef4444"},
                markers=True,
            )
            fig_line.update_traces(line_width=2.5)
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
            )
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Run predictions to see trends here.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Risk Level breakdown ───────────────────────────────────────────────
    col_risk, col_recent = st.columns([1, 1.6])

    with col_risk:
        st.markdown("#### 🎯 Risk Level Distribution")
        if total:
            risk_counts = df["risk_level"].value_counts()
            fig_bar = go.Figure(go.Bar(
                x=risk_counts.index.tolist(),
                y=risk_counts.values.tolist(),
                marker=dict(
                    color=["#ef4444" if r == "High" else "#f59e0b" if r == "Medium" else "#22c55e"
                           for r in risk_counts.index],
                    line=dict(color="rgba(0,0,0,0)", width=0),
                ),
                text=risk_counts.values.tolist(),
                textposition="outside",
                textfont=dict(color="#e6edf3"),
            ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6edf3"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=250,
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available.")

    with col_recent:
        st.markdown("#### 🕒 Recent Activity")
        if total:
            recent = df.head(8)[["created_at", "prediction", "confidence", "risk_level"]].copy()
            recent["confidence"] = recent["confidence"].apply(lambda x: f"{x:.1f}%")
            recent["created_at"] = pd.to_datetime(recent["created_at"]).dt.strftime("%b %d, %H:%M")
            recent.columns = ["Date & Time", "Diagnosis", "Confidence", "Risk"]
            st.dataframe(
                recent,
                use_container_width=True,
                height=250,
                hide_index=True,
            )
        else:
            st.info("No recent activity.")
