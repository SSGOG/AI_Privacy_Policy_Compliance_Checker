"""
ComplianceEngine: NLI-based zero-shot compliance classification.
Classifies each policy clause against GDPR/CCPA requirements using
a zero-shot classification pipeline from HuggingFace Transformers.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Supported compliance statuses
STATUS_COMPLIANT = "Fully Compliant"
STATUS_PARTIAL = "Partially Compliant"
STATUS_NON_COMPLIANT = "Non-Compliant"
STATUS_IRRELEVANT = "Not Applicable"

# Colour mapping for UI
STATUS_COLORS = {
    STATUS_COMPLIANT: "#2d9c4e",      # green
    STATUS_PARTIAL: "#e07b00",         # amber
    STATUS_NON_COMPLIANT: "#c0392b",   # red
    STATUS_IRRELEVANT: "#7f8c8d",      # grey
}

STATUS_EMOJI = {
    STATUS_COMPLIANT: "✅",
    STATUS_PARTIAL: "⚠️",
    STATUS_NON_COMPLIANT: "❌",
    STATUS_IRRELEVANT: "⬜",
}


class ComplianceEngine:
    """
    Core compliance classification engine using:
    - Zero-shot NLI via HuggingFace transformers (cross-encoder/nli-deberta-v3-small)
    - RAG pipeline for evidence retrieval
    - Threshold-based status mapping
    """

    MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
        self._classifier = None

    def _get_classifier(self):
        if self._classifier is None:
            from transformers import pipeline
            logger.info(f"Loading NLI model: {self.MODEL_NAME}")
            self._classifier = pipeline(
                "zero-shot-classification",
                model=self.MODEL_NAME,
                device=-1,          # CPU
                truncation=True,
                max_length=512,
            )
        return self._classifier

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify_clause(
        self, clause_text: str, law: str
    ) -> Dict[str, Any]:
        """
        Classify a policy clause against a specific law.

        Returns:
            {
                "status": str,          # Fully Compliant / Partially Compliant / ...
                "confidence": float,    # 0-1
                "scores": dict,         # raw scores per label
                "evidence": list,       # retrieved legal articles
                "summary": str,         # human-readable explanation
            }
        """
        if len(clause_text.strip()) < 30:
            return self._not_applicable(clause_text)

        try:
            classifier = self._get_classifier()
        except Exception as e:
            logger.warning(f"Classifier unavailable, using fallback: {e}")
            evidence = self.rag.get_evidence(clause_text, law, top_k=3)
            return self._fallback_classify(clause_text, law, evidence)

        evidence = self.rag.get_evidence(clause_text, law, top_k=3)

        # Build hypothesis template using the top retrieved requirement
        if evidence:
            top_req = evidence[0]["requirement"]
            hypothesis_template = (
                "This policy clause {} "
                + f"(Relevant requirement: {top_req[:200]})"
            )
        else:
            hypothesis_template = "This policy clause {}."

        candidate_labels = [
            "clearly addresses the legal requirement",
            "partially addresses the legal requirement but is incomplete",
            "fails to address the legal requirement",
        ]

        try:
            result = classifier(
                clause_text[:512],
                candidate_labels,
                hypothesis_template=hypothesis_template,
                multi_label=False,
            )
        except Exception as e:
            logger.warning(f"Classification error (NLI pipeline): {e}")
            return self._fallback_classify(clause_text, law, evidence)
        except BaseException as e:
            logger.warning(f"Unexpected classification error: {e}")
            return self._fallback_classify(clause_text, law, evidence)

        scores = dict(zip(result["labels"], result["scores"]))
        top_label = result["labels"][0]
        top_score = result["scores"][0]

        # Map NLI output to compliance status
        status, confidence = self._map_to_status(top_label, top_score, scores)
        summary = self._build_summary(clause_text, law, status, evidence)

        return {
            "status": status,
            "confidence": round(confidence, 3),
            "scores": {
                STATUS_COMPLIANT: round(scores.get("clearly addresses the legal requirement", 0), 3),
                STATUS_PARTIAL: round(scores.get("partially addresses the legal requirement but is incomplete", 0), 3),
                STATUS_NON_COMPLIANT: round(scores.get("fails to address the legal requirement", 0), 3),
            },
            "evidence": evidence,
            "summary": summary,
        }

    def classify_batch(
        self, clauses: List[str], law: str
    ) -> List[Dict[str, Any]]:
        """Classify a list of clauses for a given law."""
        return [self.classify_clause(clause, law) for clause in clauses]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _map_to_status(
        self, top_label: str, top_score: float, scores: Dict[str, float]
    ):
        """Convert NLI top label + score into compliance status."""
        compliant_score = scores.get("clearly addresses the legal requirement", 0)
        partial_score = scores.get("partially addresses the legal requirement but is incomplete", 0)
        non_compliant_score = scores.get("fails to address the legal requirement", 0)

        # Strong compliant signal
        if compliant_score > 0.55:
            return STATUS_COMPLIANT, compliant_score

        # Strong non-compliant signal
        if non_compliant_score > 0.55:
            return STATUS_NON_COMPLIANT, non_compliant_score

        # Partial or ambiguous
        if partial_score > 0.35 or (compliant_score > 0.30 and non_compliant_score > 0.25):
            return STATUS_PARTIAL, partial_score

        # Default based on top label
        if "clearly addresses" in top_label:
            return STATUS_COMPLIANT, top_score
        elif "fails" in top_label:
            return STATUS_NON_COMPLIANT, top_score
        else:
            return STATUS_PARTIAL, top_score

    def _build_summary(
        self,
        clause_text: str,
        law: str,
        status: str,
        evidence: List[Dict],
    ) -> str:
        """Build a human-readable compliance summary."""
        top_article = evidence[0]["article"] if evidence else "general requirements"
        top_title = evidence[0]["title"] if evidence else ""
        req_snippet = evidence[0]["requirement"][:150] if evidence else ""

        if status == STATUS_COMPLIANT:
            return (
                f"This clause appears to satisfy {law} requirements. "
                f"It is most relevant to {top_article} ({top_title}). "
                f"The clause adequately addresses: {req_snippet}"
            )
        elif status == STATUS_PARTIAL:
            return (
                f"This clause partially addresses {law} requirements but may be incomplete. "
                f"It is most relevant to {top_article} ({top_title}). "
                f"The clause should more clearly address: {req_snippet}"
            )
        else:
            return (
                f"This clause may fail to meet {law} requirements. "
                f"It is most relevant to {top_article} ({top_title}). "
                f"The clause is missing or contradicts: {req_snippet}"
            )

    def _not_applicable(self, clause_text: str) -> Dict[str, Any]:
        return {
            "status": STATUS_IRRELEVANT,
            "confidence": 1.0,
            "scores": {},
            "evidence": [],
            "summary": "Clause is too short or does not contain policy content.",
        }

    def _fallback_classify(
        self, clause_text: str, law: str, evidence: List[Dict]
    ) -> Dict[str, Any]:
        """Simple keyword-based fallback when the model fails."""
        text_lower = clause_text.lower()
        compliant_keywords = [
            "right to", "you may", "you can", "we will", "we are committed",
            "we protect", "encrypted", "secure", "consent", "lawful",
            "we provide", "you have the right",
        ]
        non_compliant_keywords = [
            "we may share with anyone", "no guarantee", "not responsible",
            "we own", "we sell your data", "no refund", "no deletion",
        ]

        compliant_hits = sum(1 for kw in compliant_keywords if kw in text_lower)
        non_compliant_hits = sum(1 for kw in non_compliant_keywords if kw in text_lower)

        if non_compliant_hits > 0:
            status = STATUS_NON_COMPLIANT
            confidence = 0.6
        elif compliant_hits >= 2:
            status = STATUS_COMPLIANT
            confidence = 0.5
        else:
            status = STATUS_PARTIAL
            confidence = 0.4

        return {
            "status": status,
            "confidence": confidence,
            "scores": {STATUS_COMPLIANT: 0.33, STATUS_PARTIAL: 0.33, STATUS_NON_COMPLIANT: 0.33},
            "evidence": evidence,
            "summary": f"Heuristic classification applied (model unavailable). Clause may {status.lower()}.",
        }
