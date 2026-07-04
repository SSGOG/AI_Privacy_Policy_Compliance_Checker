"""
Explainer: LIME and SHAP explainability for compliance classification decisions.
Identifies which words/phrases most influenced the model's compliance verdict.
"""

from __future__ import annotations
import logging
import re
from typing import Dict, Any, List, Callable, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class Explainer:
    """
    Provides LIME-based and SHAP-based explanations for compliance classifications.
    Highlights the most influential words in a policy clause.
    """

    CLASS_NAMES = ["Non-Compliant", "Partially Compliant", "Fully Compliant"]

    def __init__(self, compliance_engine):
        self.engine = compliance_engine
        self._lime_explainer = None

    def _get_lime_explainer(self):
        if self._lime_explainer is None:
            from lime.lime_text import LimeTextExplainer
            self._lime_explainer = LimeTextExplainer(
                class_names=self.CLASS_NAMES,
                random_state=42,
            )
        return self._lime_explainer

    def _make_predict_fn(self, law: str, frozen_hypothesis_template: str) -> Callable:
        """
        Create a stable predict-probability function for LIME.

        The hypothesis template is frozen from the original clause's top RAG evidence,
        so all perturbed samples are evaluated against the same fixed requirement.
        This ensures LIME attributions reflect the classifier's sensitivity to input
        words, not shifting RAG retrieval across perturbations.

        Maps text → [P(non-compliant), P(partial), P(compliant)]
        """
        engine = self.engine

        candidate_labels = [
            "clearly addresses the legal requirement",
            "partially addresses the legal requirement but is incomplete",
            "fails to address the legal requirement",
        ]

        def predict_proba(texts: List[str]) -> np.ndarray:
            results = []
            classifier = engine._get_classifier()
            for text in texts:
                if len(text.strip()) < 10:
                    results.append([1 / 3, 1 / 3, 1 / 3])
                    continue
                try:
                    out = classifier(
                        text[:512],
                        candidate_labels,
                        hypothesis_template=frozen_hypothesis_template,
                        multi_label=False,
                    )
                    scores = dict(zip(out["labels"], out["scores"]))
                    p_compliant = scores.get("clearly addresses the legal requirement", 0.33)
                    p_partial = scores.get(
                        "partially addresses the legal requirement but is incomplete", 0.33
                    )
                    p_non = scores.get("fails to address the legal requirement", 0.33)
                except Exception:
                    p_compliant = p_partial = p_non = 1 / 3

                total = p_compliant + p_partial + p_non
                if total > 0:
                    p_compliant /= total
                    p_partial /= total
                    p_non /= total

                results.append([p_non, p_partial, p_compliant])
            return np.array(results)

        return predict_proba

    # ------------------------------------------------------------------
    # LIME explanation
    # ------------------------------------------------------------------

    def explain_lime(
        self,
        clause_text: str,
        law: str,
        classification_result: Dict[str, Any],
        num_features: int = 12,
        num_samples: int = 80,
    ) -> Dict[str, Any]:
        """
        Generate a LIME explanation for a clause classification.

        Returns:
            {
                "method": "LIME",
                "top_features": list of (word, weight) tuples,
                "html": str,              # LIME HTML highlight
                "textual_summary": str,   # human-readable explanation
                "predicted_class": str,
                "class_probs": dict,
            }
        """
        status = classification_result.get("status", "Unknown")
        scores = classification_result.get("scores", {})

        # Predicted class index (for LIME)
        status_to_idx = {
            "Non-Compliant": 0,
            "Partially Compliant": 1,
            "Fully Compliant": 2,
        }
        predicted_idx = status_to_idx.get(status, 1)

        # Freeze the hypothesis from the original clause's top RAG evidence
        # so all LIME perturbation calls use the same requirement — not re-retrieved.
        evidence = classification_result.get("evidence", [])
        if evidence:
            top_req = evidence[0]["requirement"][:200]
            frozen_hypothesis = (
                "This policy clause {} "
                + f"(Relevant requirement: {top_req})"
            )
        else:
            frozen_hypothesis = "This policy clause {}."

        predict_fn = self._make_predict_fn(law, frozen_hypothesis)

        try:
            lime_explainer = self._get_lime_explainer()
            explanation = lime_explainer.explain_instance(
                clause_text,
                predict_fn,
                num_features=num_features,
                num_samples=num_samples,
                labels=(predicted_idx,),
            )

            feature_importance = explanation.as_list(label=predicted_idx)
            html_output = explanation.as_html()

            # Build textual summary
            positive_words = [
                f"'{w}' (+{w:.3f})" if not isinstance(w, str) else f"'{w}'"
                for w, weight in feature_importance
                if weight > 0
            ][:5]
            negative_words = [
                f"'{w}'"
                for w, weight in feature_importance
                if weight < 0
            ][:5]

            textual_summary = self._build_lime_summary(
                clause_text, law, status, feature_importance
            )

            return {
                "method": "LIME",
                "top_features": feature_importance,
                "html": html_output,
                "textual_summary": textual_summary,
                "predicted_class": status,
                "class_probs": {
                    "Non-Compliant": round(scores.get("Non-Compliant", 0), 3),
                    "Partially Compliant": round(scores.get("Partially Compliant", 0), 3),
                    "Fully Compliant": round(scores.get("Fully Compliant", 0), 3),
                },
            }

        except Exception as e:
            logger.warning(f"LIME explanation failed: {e}")
            return self._fallback_explanation(clause_text, law, status, scores)

    # ------------------------------------------------------------------
    # Plotly feature importance chart
    # ------------------------------------------------------------------

    def build_feature_chart(
        self, top_features: List[Tuple[str, float]], title: str = "LIME Feature Importance"
    ):
        """Build a Plotly horizontal bar chart of LIME feature weights."""
        try:
            import plotly.graph_objects as go

            if not top_features:
                return None

            words = [f[0] for f in top_features]
            weights = [f[1] for f in top_features]
            colors = [
                "#2d9c4e" if w > 0 else "#c0392b" for w in weights
            ]

            fig = go.Figure(
                go.Bar(
                    x=weights,
                    y=words,
                    orientation="h",
                    marker_color=colors,
                    text=[f"{w:+.3f}" for w in weights],
                    textposition="outside",
                )
            )
            fig.update_layout(
                title=title,
                xaxis_title="Weight (positive = supports compliance)",
                yaxis={"autorange": "reversed"},
                height=max(300, len(top_features) * 30 + 80),
                margin=dict(l=20, r=60, t=50, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            return fig
        except Exception as e:
            logger.warning(f"Chart build failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Keyword-based highlight (no model needed)
    # ------------------------------------------------------------------

    def highlight_text(
        self, clause_text: str, top_features: List[Tuple[str, float]]
    ) -> str:
        """
        Return HTML with words highlighted based on LIME feature weights.
        Green = supports compliance, red = undermines compliance.
        """
        if not top_features:
            return clause_text

        highlighted = clause_text
        for word, weight in sorted(top_features, key=lambda x: abs(x[1]), reverse=True):
            clean_word = re.escape(str(word))
            if weight > 0.01:
                color = "#c8f7c5"
                border = "#27ae60"
            elif weight < -0.01:
                color = "#f7c5c5"
                border = "#c0392b"
            else:
                continue
            replacement = (
                f'<mark style="background-color:{color};border-bottom:2px solid {border};'
                f'border-radius:2px;padding:0 2px;" title="Weight: {weight:+.3f}">'
                f"{word}</mark>"
            )
            highlighted = re.sub(
                r"\b" + clean_word + r"\b",
                replacement,
                highlighted,
                flags=re.IGNORECASE,
                count=1,
            )
        return highlighted

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_lime_summary(
        self,
        clause_text: str,
        law: str,
        status: str,
        feature_importance: List[Tuple[str, float]],
    ) -> str:
        supporting = [w for w, weight in feature_importance if weight > 0.02][:4]
        opposing = [w for w, weight in feature_importance if weight < -0.02][:4]

        if status == "Fully Compliant":
            base = f"The clause is classified as **Fully Compliant** with {law}."
        elif status == "Partially Compliant":
            base = f"The clause is classified as **Partially Compliant** with {law}."
        else:
            base = f"The clause is classified as **Non-Compliant** with {law}."

        parts = [base]
        if supporting:
            parts.append(
                f"Key terms that support compliance: *{', '.join(supporting)}*."
            )
        if opposing:
            parts.append(
                f"Terms that weaken the compliance signal: *{', '.join(opposing)}*."
            )
        if not supporting and not opposing:
            parts.append(
                "The classification is based on the overall context; no single term dominates."
            )
        return " ".join(parts)

    def _fallback_explanation(
        self,
        clause_text: str,
        law: str,
        status: str,
        scores: Dict,
    ) -> Dict[str, Any]:
        """Keyword-based fallback when LIME cannot run."""
        words = re.findall(r"\b\w+\b", clause_text)
        positive_kw = {
            "consent", "right", "access", "secure", "protect", "delete",
            "erasure", "transparent", "lawful", "notify", "encrypt", "opt-out",
        }
        negative_kw = {
            "sell", "share", "unlimited", "forever", "irrevocable", "waive",
            "no", "not", "cannot", "refuse", "deny",
        }
        features = []
        seen = set()
        for word in words:
            wl = word.lower()
            if wl in seen:
                continue
            seen.add(wl)
            if wl in positive_kw:
                features.append((word, 0.15))
            elif wl in negative_kw:
                features.append((word, -0.10))

        summary = (
            f"Keyword-based explanation (LIME unavailable): "
            f"The clause is classified as **{status}** with {law}. "
        )
        if features:
            pos = [w for w, s in features if s > 0]
            neg = [w for w, s in features if s < 0]
            if pos:
                summary += f"Compliance-supporting terms: {', '.join(pos[:4])}. "
            if neg:
                summary += f"Risk terms: {', '.join(neg[:4])}."

        return {
            "method": "Keyword Heuristic",
            "top_features": features[:12],
            "html": None,
            "textual_summary": summary,
            "predicted_class": status,
            "class_probs": scores,
        }
