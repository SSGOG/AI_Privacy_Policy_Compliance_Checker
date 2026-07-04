"""
Compliance analysis service — model loading and analysis logic (no Streamlit).
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from utils import (
    build_csv_report,
    build_pdf_report,
    compute_summary_stats,
    extract_text_from_pdf,
    extract_text_from_txt,
    segment_clauses,
)

logger = logging.getLogger(__name__)

CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")


@lru_cache(maxsize=1)
def get_rag_pipeline():
    from rag_pipeline import RAGPipeline
    return RAGPipeline(persist_dir=CHROMA_DIR)


@lru_cache(maxsize=1)
def get_compliance_engine():
    from compliance_engine import ComplianceEngine
    return ComplianceEngine(get_rag_pipeline())


@lru_cache(maxsize=1)
def get_explainer():
    from explainer import Explainer
    return Explainer(get_compliance_engine())


def warm_models() -> None:
    pass  # lazy load — models load on first request to save startup RAM


def parse_document(filename: str, raw_bytes: bytes) -> tuple[str, list[str]]:
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(raw_bytes)
    elif filename.lower().endswith(".txt"):
        text = extract_text_from_txt(raw_bytes)
    else:
        raise ValueError("Unsupported file type. Upload PDF or TXT.")

    if not text.strip():
        raise ValueError("The document appears to be empty or could not be parsed.")

    clauses = segment_clauses(text)
    if not clauses:
        raise ValueError("No clauses could be extracted from the document.")

    policy_name = filename.rsplit(".", 1)[0]
    return policy_name, clauses


def analyze_clauses(
    clauses: list[str],
    laws: list[str],
    top_k_evidence: int = 3,
) -> dict[str, list[dict[str, Any]]]:
    engine = get_compliance_engine()
    rag = get_rag_pipeline()
    results_by_law: dict[str, list[dict[str, Any]]] = {}

    for law in laws:
        law_results = []
        for clause in clauses:
            result = engine.classify_clause(clause, law)
            result["evidence"] = rag.get_evidence(clause, law, top_k=top_k_evidence)
            law_results.append(_serialize_result(result))
        results_by_law[law] = law_results

    return results_by_law


def analyze_sample_clause(
    clause: str,
    laws: list[str],
    top_k_evidence: int = 3,
) -> dict[str, dict[str, Any]]:
    engine = get_compliance_engine()
    rag = get_rag_pipeline()
    results: dict[str, dict[str, Any]] = {}

    for law in laws:
        result = engine.classify_clause(clause, law)
        result["evidence"] = rag.get_evidence(clause, law, top_k=top_k_evidence)
        results[law] = _serialize_result(result)

    return results


def explain_clause(
    clause: str,
    law: str,
    result: dict[str, Any],
    num_samples: int = 60,
) -> dict[str, Any]:
    explainer = get_explainer()
    exp = explainer.explain_lime(clause, law, result, num_samples=num_samples)
    features = exp.get("top_features", [])

    chart_data = []
    if features:
        chart_data = [
            {"word": word, "weight": float(weight)}
            for word, weight in features
        ]

    highlighted = explainer.highlight_text(clause, features) if features else clause

    return {
        "textual_summary": exp.get("textual_summary", ""),
        "top_features": chart_data,
        "highlighted_text": highlighted,
    }


def build_analysis_response(
    policy_name: str,
    clauses: list[str],
    results_by_law: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    stats = compute_summary_stats(results_by_law)
    return {
        "policy_name": policy_name,
        "clauses": clauses,
        "results_by_law": results_by_law,
        "stats": stats,
    }


def generate_csv(clauses: list[str], results_by_law: dict, policy_name: str) -> bytes:
    return build_csv_report(clauses, results_by_law, policy_name)


def generate_pdf(clauses: list[str], results_by_law: dict, policy_name: str) -> bytes:
    return build_pdf_report(clauses, results_by_law, policy_name)


def _serialize_result(result: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "status": result.get("status", "Unknown"),
        "confidence": float(result.get("confidence", 0)),
        "summary": result.get("summary", ""),
        "scores": {k: float(v) for k, v in (result.get("scores") or {}).items()},
        "evidence": [],
    }
    for ev in result.get("evidence") or []:
        serialized["evidence"].append(
            {
                "article": ev.get("article", ""),
                "title": ev.get("title", ""),
                "text": ev.get("text", ""),
                "requirement": ev.get("requirement", ""),
                "similarity": float(ev.get("similarity", 0)),
            }
        )
    return serialized
