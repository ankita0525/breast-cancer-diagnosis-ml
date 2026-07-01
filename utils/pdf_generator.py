import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Colour palette ─────────────────────────────────────────────────────────
C_PRIMARY   = colors.HexColor("#6C63FF")
C_ACCENT    = colors.HexColor("#FF6584")
C_DARK      = colors.HexColor("#0d1117")
C_CARD      = colors.HexColor("#1f2937")
C_GREEN     = colors.HexColor("#22c55e")
C_RED       = colors.HexColor("#ef4444")
C_YELLOW    = colors.HexColor("#f59e0b")
C_TEXT      = colors.HexColor("#1e293b")
C_MUTED     = colors.HexColor("#64748b")
C_WHITE     = colors.white


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=22,
            textColor=C_PRIMARY, alignment=TA_CENTER, spaceAfter=4
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=10,
            textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=2
        ),
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=12,
            textColor=C_PRIMARY, spaceBefore=14, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10,
            textColor=C_TEXT, leading=16
        ),
        "small": ParagraphStyle(
            "small", fontName="Helvetica", fontSize=8,
            textColor=C_MUTED, alignment=TA_CENTER
        ),
        "warning": ParagraphStyle(
            "warning", fontName="Helvetica-Bold", fontSize=11,
            textColor=C_RED, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8
        ),
    }


def generate_pdf_report(
    patient_name: str,
    patient_email: str,
    prediction: str,
    confidence: float,
    risk_level: str,
    prob_malignant: float,
    prob_benign: float,
    prediction_id: int = None,
) -> str:
    """Generate a PDF report and return the file path."""

    fname   = f"report_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    fpath   = os.path.join(REPORTS_DIR, fname)

    doc = SimpleDocTemplate(
        fpath,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )

    styles  = _styles()
    story   = []
    W       = A4[0] - 4*cm   # usable width

    # ── Header banner ──────────────────────────────────────────────────────
    header_data = [
        [Paragraph("🩺  OncoSight Diagnostic Report", styles["title"])],
        [Paragraph("Breast Cancer Diagnostic Platform — Confidential Medical Record",
                   styles["subtitle"])],
    ]
    header_tbl = Table(header_data, colWidths=[W])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_PRIMARY),
        ("TEXTCOLOR",  (0, 0), (-1, -1), C_WHITE),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 18))

    # ── Report metadata ────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    meta_data = [
        ["Report ID:",     f"RPT-{prediction_id or '—'}"],
        ["Generated:",     now_str],
        ["Patient Name:",  patient_name],
        ["Patient Email:", patient_email],
    ]
    meta_tbl = Table(meta_data, colWidths=[W * 0.3, W * 0.7])
    meta_tbl.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("TEXTCOLOR",   (0,0), (0,-1), C_MUTED),
        ("TEXTCOLOR",   (1,0), (1,-1), C_TEXT),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [colors.HexColor("#f8fafc"), C_WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width=W, color=colors.HexColor("#e2e8f0"), thickness=1))
    story.append(Spacer(1, 14))

    # ── Diagnosis Result ───────────────────────────────────────────────────
    story.append(Paragraph("Diagnostic Result", styles["section"]))

    result_color  = C_RED if prediction == "Malignant" else C_GREEN
    risk_color    = {
        "High":   C_RED,
        "Medium": C_YELLOW,
        "Low":    C_GREEN,
    }.get(risk_level, C_MUTED)

    result_data = [
        ["Diagnosis",       "Confidence Score",  "Risk Level"],
        [
            Paragraph(f'<font color="{"#ef4444" if prediction=="Malignant" else "#22c55e"}">'
                      f'<b>{prediction}</b></font>', styles["body"]),
            Paragraph(f"<b>{confidence:.1f}%</b>", styles["body"]),
            Paragraph(f'<font color="{"#ef4444" if risk_level=="High" else "#f59e0b" if risk_level=="Medium" else "#22c55e"}">'
                      f'<b>{risk_level} Risk</b></font>', styles["body"]),
        ]
    ]
    res_tbl = Table(result_data, colWidths=[W/3, W/3, W/3])
    res_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_PRIMARY),
        ("TEXTCOLOR",     (0,0),(-1,0), C_WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 11),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("BACKGROUND",    (0,1),(-1,1), colors.HexColor("#f0f4ff")),
        ("BOX",           (0,0),(-1,-1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(res_tbl)
    story.append(Spacer(1, 14))

    # ── Probability Breakdown ──────────────────────────────────────────────
    story.append(Paragraph("Probability Analysis", styles["section"]))
    prob_data = [
        ["Classification",    "Probability",    "Interpretation"],
        ["Benign (Non-Cancer)",  f"{prob_benign:.1f}%",
         "Tumor appears non-cancerous" if prob_benign > 50 else "Lower likelihood"],
        ["Malignant (Cancer)", f"{prob_malignant:.1f}%",
         "High cancer risk — urgent review" if prob_malignant >= 75 else
         "Moderate risk — further tests advised" if prob_malignant >= 50 else
         "Lower malignancy likelihood"],
    ]
    prob_tbl = Table(prob_data, colWidths=[W*0.35, W*0.2, W*0.45])
    prob_tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0), C_CARD),
        ("TEXTCOLOR",      (0,0),(-1,0), C_WHITE),
        ("FONTNAME",       (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",       (0,0),(-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.HexColor("#f8fafc"), C_WHITE]),
        ("TOPPADDING",     (0,0),(-1,-1), 9),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 9),
        ("LEFTPADDING",    (0,0),(-1,-1), 10),
        ("BOX",            (0,0),(-1,-1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(prob_tbl)
    story.append(Spacer(1, 14))

    # ── Clinical Recommendation ────────────────────────────────────────────
    story.append(Paragraph("Clinical Recommendation", styles["section"]))
    if prediction == "Malignant":
        rec_text = (
            "⚠️  The model indicates a <b>Malignant</b> tumor with high confidence. "
            "It is strongly recommended that the patient undergo immediate clinical review "
            "by a qualified oncologist. Additional diagnostic procedures such as biopsy, "
            "MRI, or CT scan should be considered to confirm this result. "
            "Early detection and treatment significantly improves patient outcomes."
        )
    else:
        rec_text = (
            "✅  The model indicates a <b>Benign</b> tumor. "
            "While this is a favourable result, it is recommended to continue regular "
            "monitoring and follow-up examinations as advised by a healthcare professional. "
            "This report is a diagnostic aid and should not replace professional medical advice."
        )
    story.append(Paragraph(rec_text, styles["body"]))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width=W, color=colors.HexColor("#e2e8f0"), thickness=1))
    story.append(Spacer(1, 10))

    # ── Disclaimer ─────────────────────────────────────────────────────────
    disclaimer = (
        "DISCLAIMER: This report is generated by an AI-assisted diagnostic tool trained on the "
        "Wisconsin Diagnostic Breast Cancer (WDBC) dataset. It is intended for educational and "
        "supportive purposes only and must NOT be used as the sole basis for clinical decisions. "
        "Always consult a qualified medical professional."
    )
    story.append(Paragraph(disclaimer, styles["small"]))

    doc.build(story)
    return fpath
