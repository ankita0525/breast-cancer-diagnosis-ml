import streamlit as st


def inject_global_css():
    st.markdown("""
<style>
/* ── Google Font ───────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ────────────────────────────────────────────────────── */
:root {
    --primary:     #6C63FF;
    --primary-d:   #574fd6;
    --accent:      #FF6584;
    --success:     #22c55e;
    --warning:     #f59e0b;
    --danger:      #ef4444;
    --bg-dark:     #0d1117;
    --bg-card:     #161b22;
    --bg-card2:    #1f2937;
    --border:      rgba(255,255,255,0.08);
    --text-main:   #e6edf3;
    --text-muted:  #8b949e;
    --gradient1:   linear-gradient(135deg, #6C63FF 0%, #FF6584 100%);
    --gradient2:   linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    --shadow:      0 8px 32px rgba(0,0,0,0.4);
    --radius:      14px;
}

/* ── Global Reset ──────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App Background ────────────────────────────────────────────────────── */
.stApp {
    background: var(--gradient2) !important;
    color: var(--text-main) !important;
    min-height: 100vh;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

/* ── Hide default Streamlit elements ───────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Buttons ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--gradient1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.6rem !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(108,99,255,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Inputs ────────────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input,
.stSelectbox select, .stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-main) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.25) !important;
}

/* ── Metric cards ──────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.2rem 1.5rem !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Dataframe ─────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ── Tabs ──────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card2) !important;
    border-radius: 10px !important;
    gap: 4px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-muted) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: #fff !important;
}

/* ── Custom Card ───────────────────────────────────────────────────────── */
.onco-card {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.onco-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}

.onco-hero {
    background: var(--gradient1);
    border-radius: var(--radius);
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.onco-hero h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #fff;
    margin: 0;
    letter-spacing: -0.5px;
}
.onco-hero p {
    color: rgba(255,255,255,0.85);
    margin-top: 0.5rem;
    font-size: 1.05rem;
}

.badge-benign {
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 20px;
    padding: 4px 14px;
    font-weight: 600;
    font-size: 0.88rem;
}
.badge-malignant {
    background: rgba(239,68,68,0.15);
    color: #ef4444;
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 20px;
    padding: 4px 14px;
    font-weight: 600;
    font-size: 0.88rem;
}
.badge-high   { background:rgba(239,68,68,0.15);  color:#ef4444;  border:1px solid rgba(239,68,68,0.3);  border-radius:20px; padding:3px 12px; font-weight:600; }
.badge-medium { background:rgba(245,158,11,0.15); color:#f59e0b;  border:1px solid rgba(245,158,11,0.3); border-radius:20px; padding:3px 12px; font-weight:600; }
.badge-low    { background:rgba(34,197,94,0.15);  color:#22c55e;  border:1px solid rgba(34,197,94,0.3);  border-radius:20px; padding:3px 12px; font-weight:600; }

.stat-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 0.2rem;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
}

/* ── Spinner ───────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Progress ──────────────────────────────────────────────────────────── */
.stProgress > div > div {
    background: var(--gradient1) !important;
    border-radius: 10px !important;
}

/* ── Alert / Info ──────────────────────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius) !important;
}

/* ── Divider ───────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 6px; }
</style>
""", unsafe_allow_html=True)
