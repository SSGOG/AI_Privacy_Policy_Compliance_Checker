"""
Utilities: PDF parsing, clause segmentation, and report generation.
"""

from __future__ import annotations
import re
import io
import logging
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PDF Parsing
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF uploaded as bytes."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise ValueError(f"Could not read PDF: {e}")


def extract_text_from_txt(text_bytes: bytes) -> str:
    """Extract text from a plain-text file uploaded as bytes."""
    try:
        return text_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Could not read text file: {e}")


# ---------------------------------------------------------------------------
# Clause Segmentation
# ---------------------------------------------------------------------------

# Minimum and maximum clause character lengths
MIN_CLAUSE_LEN = 60
MAX_CLAUSE_LEN = 1200
TARGET_CLAUSE_LEN = 400


def segment_clauses(text: str) -> List[str]:
    """
    Segment a privacy policy into meaningful clauses.

    Strategy:
    1. Split on paragraph boundaries (double newlines or numbered/bulleted items).
    2. Merge very short fragments into the previous clause.
    3. Split very long clauses at sentence boundaries.
    """
    # Normalise whitespace
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # Split on paragraph or section boundaries
    raw_segments = re.split(r"\n{2,}", text)

    # Sub-split on numbered / bulleted items
    refined: List[str] = []
    for seg in raw_segments:
        sub = re.split(r"\n(?=\s*[\d]+[\.\)]\s|\s*[•\-–]\s)", seg)
        for s in sub:
            s = s.strip()
            if s:
                refined.append(s)

    # Merge or split to approach TARGET_CLAUSE_LEN
    clauses = _merge_short(refined)
    clauses = _split_long(clauses)

    # Final filter
    clauses = [c.strip() for c in clauses if len(c.strip()) >= MIN_CLAUSE_LEN]
    return clauses


def _merge_short(segments: List[str]) -> List[str]:
    """Merge consecutive short segments."""
    merged = []
    buffer = ""
    for seg in segments:
        if len(buffer) + len(seg) < TARGET_CLAUSE_LEN:
            buffer = (buffer + "\n" + seg).strip() if buffer else seg
        else:
            if buffer:
                merged.append(buffer)
            buffer = seg
    if buffer:
        merged.append(buffer)
    return merged


def _split_long(segments: List[str]) -> List[str]:
    """Split excessively long segments at sentence boundaries."""
    result = []
    for seg in segments:
        if len(seg) <= MAX_CLAUSE_LEN:
            result.append(seg)
            continue
        # Split at sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", seg)
        chunk = ""
        for sent in sentences:
            if len(chunk) + len(sent) < MAX_CLAUSE_LEN:
                chunk = (chunk + " " + sent).strip()
            else:
                if chunk:
                    result.append(chunk)
                chunk = sent
        if chunk:
            result.append(chunk)
    return result


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def build_report_df(
    clauses: List[str],
    results_by_law: dict,
) -> pd.DataFrame:
    """
    Build a pandas DataFrame with clause analysis results.

    Args:
        clauses: List of clause strings.
        results_by_law: Dict mapping law name → list of classification results.

    Returns:
        DataFrame with columns: Clause, [Law] Status, [Law] Confidence, [Law] Summary, ...
    """
    rows = []
    for idx, clause in enumerate(clauses):
        row = {"Clause #": idx + 1, "Clause Text": clause[:300] + "..." if len(clause) > 300 else clause}
        for law, results in results_by_law.items():
            if idx < len(results):
                r = results[idx]
                row[f"{law} Status"] = r.get("status", "")
                row[f"{law} Confidence"] = f"{r.get('confidence', 0):.1%}"
                row[f"{law} Top Article"] = (
                    r["evidence"][0]["article"] if r.get("evidence") else ""
                )
                row[f"{law} Summary"] = r.get("summary", "")[:250]
        rows.append(row)
    return pd.DataFrame(rows)


def build_csv_report(
    clauses: List[str],
    results_by_law: dict,
    policy_name: str = "Privacy Policy",
) -> bytes:
    """Return the compliance report as CSV bytes."""
    df = build_report_df(clauses, results_by_law)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Unicode → Latin-1 sanitisation for fpdf2 / Helvetica
# ---------------------------------------------------------------------------
import unicodedata as _unicodedata

# Explicit map for characters that survive NFKD but are still outside Latin-1,
# plus common "smart" punctuation that should become plain ASCII.
_UNICODE_TO_LATIN1 = str.maketrans({
    # Smart / curly quotes
    "\u2018": "'",    # left single quotation mark
    "\u2019": "'",    # right single quotation mark  ← the original crash char
    "\u201A": "'",    # single low-9 quotation mark
    "\u201B": "'",    # single high-reversed-9 quotation mark
    "\u201C": '"',    # left double quotation mark
    "\u201D": '"',    # right double quotation mark
    "\u201E": '"',    # double low-9 quotation mark
    "\u201F": '"',    # double high-reversed-9 quotation mark
    # Dashes
    "\u2013": "-",    # en dash
    "\u2014": "--",   # em dash
    "\u2015": "--",   # horizontal bar
    "\u2212": "-",    # minus sign
    # Ellipsis / dots
    "\u2026": "...",  # horizontal ellipsis
    "\u2027": ".",    # hyphenation point
    # Bullets / list markers
    "\u2022": "*",    # bullet
    "\u2023": "*",    # triangular bullet
    "\u25CF": "*",    # black circle
    "\u25E6": "*",    # white bullet
    # Spaces / invisible chars
    "\u00A0": " ",    # non-breaking space
    "\u200B": "",     # zero-width space
    "\u200C": "",     # zero-width non-joiner
    "\u200D": "",     # zero-width joiner
    "\u2002": " ",    # en space
    "\u2003": " ",    # em space
    "\u2009": " ",    # thin space
    "\uFEFF": "",     # byte order mark / zero-width no-break space
    # Common symbols outside Latin-1
    "\u2122": "(TM)", # trade mark sign
    "\u20AC": "EUR",  # euro sign
    "\u2020": "+",    # dagger
    "\u2021": "++",   # double dagger
    "\u2030": "%o",   # per mille sign
    "\u2039": "<",    # single left-pointing angle quotation mark
    "\u203A": ">",    # single right-pointing angle quotation mark
    "\u00B7": ".",    # middle dot (actually Latin-1, kept for safety)
    "\u2010": "-",    # hyphen
    "\u2011": "-",    # non-breaking hyphen
})


def _safe_pdf(text: str) -> str:
    """Return a Latin-1-safe version of *text* suitable for Helvetica in fpdf2.

    Strategy:
    1. Apply the explicit Unicode→ASCII replacement table (handles smart quotes,
       dashes, ellipses, bullets, etc.).
    2. NFKD-normalise (decomposes accented chars like é into e + combining mark).
    3. Encode to Latin-1 with 'replace' so any remaining out-of-range codepoint
       becomes '?' rather than raising an exception.
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.translate(_UNICODE_TO_LATIN1)
    text = _unicodedata.normalize("NFKD", text)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


def build_pdf_report(
    clauses: List[str],
    results_by_law: dict,
    policy_name: str = "Privacy Policy",
) -> bytes:
    """Return the compliance report as a PDF using fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is not installed. Install it with: pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _safe_pdf("Privacy Policy Compliance Report"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, _safe_pdf(f"Document: {policy_name}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # Disclaimer
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_fill_color(255, 243, 205)
    pdf.multi_cell(
        0, 6,
        _safe_pdf(
            "DISCLAIMER: This report is generated by an AI research tool and does not "
            "constitute legal advice. It should be reviewed by a qualified legal professional."
        ),
        fill=True,
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(6)

    status_colors = {
        "Fully Compliant": (45, 156, 78),
        "Partially Compliant": (224, 123, 0),
        "Non-Compliant": (192, 57, 43),
        "Not Applicable": (127, 140, 141),
    }

    for idx, clause in enumerate(clauses):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, _safe_pdf(f"Clause {idx + 1}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        display_clause = clause[:400] + "..." if len(clause) > 400 else clause
        pdf.multi_cell(0, 5, _safe_pdf(display_clause), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        for law, results in results_by_law.items():
            if idx >= len(results):
                continue
            r = results[idx]
            status = r.get("status", "Unknown")
            rgb = status_colors.get(status, (128, 128, 128))
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*rgb)
            pdf.cell(
                0, 6,
                _safe_pdf(f"  {law}: {status} (confidence: {r.get('confidence', 0):.1%})"),
                new_x="LMARGIN", new_y="NEXT",
            )
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 8)
            summary = r.get("summary", "")[:300]
            if summary:
                pdf.multi_cell(0, 5, _safe_pdf(f"  {summary}"), new_x="LMARGIN", new_y="NEXT")
            if r.get("evidence"):
                ev = r["evidence"][0]
                pdf.multi_cell(
                    0, 5,
                    _safe_pdf(f"  Most relevant: {ev['article']} - {ev['title']}"),
                    new_x="LMARGIN", new_y="NEXT",
                )
            pdf.ln(2)

        pdf.ln(4)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def compute_summary_stats(
    results_by_law: dict,
) -> dict:
    """
    Compute summary statistics for each law.

    Returns:
        {
            "GDPR": {"total": int, "compliant": int, "partial": int, "non_compliant": int, "score": float},
            ...
        }
    """
    stats = {}
    for law, results in results_by_law.items():
        total = len(results)
        compliant = sum(1 for r in results if r.get("status") == "Fully Compliant")
        partial = sum(1 for r in results if r.get("status") == "Partially Compliant")
        non_compliant = sum(1 for r in results if r.get("status") == "Non-Compliant")
        irrelevant = total - compliant - partial - non_compliant
        effective_total = total - irrelevant
        score = (compliant + 0.5 * partial) / effective_total if effective_total > 0 else 0.0
        stats[law] = {
            "total": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": non_compliant,
            "irrelevant": irrelevant,
            "score": round(score, 3),
        }
    return stats
