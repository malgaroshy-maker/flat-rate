"""PDF generator with Arabic RTL support using reportlab + embedded Noto Naskh Arabic."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_AR = "NotoNaskhArabic"
FONT_AR_BOLD = "NotoNaskhArabic"
TTF_PATH = FONT_DIR / "NotoNaskhArabic-Regular.ttf"

if TTF_PATH.exists():
    pdfmetrics.registerFont(TTFont(FONT_AR, str(TTF_PATH)))
    pdfmetrics.registerFont(TTFont(FONT_AR_BOLD, str(TTF_PATH)))
else:
    FONT_AR = "Helvetica"
    FONT_AR_BOLD = "Helvetica-Bold"

PAGE_W, PAGE_H = landscape(A4)


def _rtl_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _has_arabic(text: str) -> bool:
    return any("\u0600" <= c <= "\u06ff" for c in text)


def _normal_style(font_size: int = 10) -> ParagraphStyle:
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        "Normal_AR",
        parent=styles["Normal"],
        fontName=FONT_AR,
        fontSize=font_size,
        leading=font_size * 1.6,
    )


def _heading_style(font_size: int = 14) -> ParagraphStyle:
    return ParagraphStyle(
        "Heading_AR",
        parent=_normal_style(font_size),
        fontName=FONT_AR_BOLD,
        spaceAfter=8,
    )


def _p(text: str, style=None) -> Paragraph:
    if style is None:
        style = _normal_style()
    return Paragraph(_rtl_text(text) if _has_arabic(text) else text, style)


def generate_pdf(
    query_text: str,
    hits: list[dict],
    confidence_range: dict[str, float],
    outliers: list[dict],
    language: str = "ar",
) -> bytes:
    is_ar = _has_arabic(query_text)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    story = []

    # Title
    title = "تقرير تقدير تكلفة العمل" if is_ar else "Labor Cost Estimate Report"
    story.append(Paragraph(_rtl_text(title), _heading_style(16)))
    story.append(Spacer(1, 0.5 * cm))

    # Query
    label_q = _rtl_text("الاستفسار:") if is_ar else "Query:"
    story.append(Paragraph(label_q, _heading_style(11)))
    story.append(_p(query_text, _normal_style(10)))
    story.append(Spacer(1, 0.3 * cm))

    # Date
    today = date.today().strftime("%Y-%m-%d")
    date_label = _rtl_text(f"التاريخ: {today}") if is_ar else f"Date: {today}"
    story.append(Paragraph(date_label, _normal_style(9)))
    story.append(Spacer(1, 0.5 * cm))

    # Confidence interval
    cr = confidence_range
    if cr:
        conf_label = _rtl_text("نطاق الثقة:") if is_ar else "Confidence Range:"
        conf_val = f"{cr.get('p10', '-')} – {cr.get('p90', '-')} {_rtl_text('ساعة') if is_ar else 'hours'}"
        story.append(Paragraph(conf_label, _heading_style(11)))
        story.append(Paragraph(conf_val, _normal_style(12)))
        median_val = f"{_rtl_text('المتوسط:') if is_ar else 'Median:'} {cr.get('p50', '-')}h"
        story.append(Paragraph(median_val, _normal_style(10)))

        # Cost estimate
        if hits and hits[0].get("price_mean", 0) > 0:
            rate = hits[0].get("price_mean", 0)
            p10_cost = cr.get("p10", 0) * rate
            p50_cost = cr.get("p50", 0) * rate
            p90_cost = cr.get("p90", 0) * rate
            cost_label = _rtl_text("التكلفة التقديرية:") if is_ar else "Estimated Cost:"
            cost_val = f"{p10_cost:.0f} – {p90_cost:.0f} LYD ({_rtl_text('المتوسط') if is_ar else 'median'}: {p50_cost:.0f} LYD)"
            story.append(Paragraph(cost_label, _heading_style(11)))
            story.append(Paragraph(cost_val, _normal_style(12)))
        story.append(Spacer(1, 0.4 * cm))

    # Hits table
    tbl_label = _rtl_text("السجلات المطابقة:") if is_ar else "Matching Records:"
    story.append(Paragraph(tbl_label, _heading_style(11)))
    story.append(Spacer(1, 0.2 * cm))

    if hits:
        h_model = _rtl_text("الموديل") if is_ar else "Model"
        h_rate = _rtl_text("السعر/س") if is_ar else "Rate/h"
        h_records = _rtl_text("السجلات") if is_ar else "Recs"
        h_hours = _rtl_text("الساعات") if is_ar else "Hours"
        h_cost = _rtl_text("التكلفة") if is_ar else "Cost"

        tbl_data = [[h_model, h_rate, h_records, h_hours, h_cost]]
        for h in hits:
            rate = h.get("price_mean", 0) or 0
            p50 = h.get("qty_median", 0) or 0
            p10 = h.get("confidence_range", {}).get("p10", 0) or 0
            p90 = h.get("confidence_range", {}).get("p90", 0) or 0
            cost_p50 = p50 * rate
            tbl_data.append([
                h.get("model", ""),
                f"{rate:.0f} LYD",
                str(h.get("qty_count", "")),
                f"{p10:.1f}–{p90:.1f}h",
                f"{cost_p50:.0f} LYD",
            ])

        tbl = Table(tbl_data, colWidths=[4 * cm, 2.5 * cm, 2 * cm, 4 * cm, 3 * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, -1), FONT_AR),
            ("FONTNAME", (0, 0), (-1, 0), FONT_AR_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)

    # Outliers
    if outliers:
        story.append(Spacer(1, 0.5 * cm))
        out_label = _rtl_text("تنبيهات القيم الشاذة:") if is_ar else "Outlier Notices:"
        story.append(Paragraph(out_label, _heading_style(11)))
        for o in outliers:
            for a in o.get("anomalies", []):
                out_text = f"{o.get('model', '')}: {a.get('value', '')}h ({a.get('deviation', '')}\u03c3)"
                story.append(Paragraph(out_text, _normal_style(9)))

    doc.build(story)
    return buf.getvalue()
