---
name: LIME Frozen Hypothesis for RAG+NLI Pipelines
description: LIME predict_fn must freeze the RAG hypothesis before perturbations to produce faithful explanations
---

**Rule:** When using LIME with a pipeline that combines RAG retrieval + NLI classification, the RAG evidence must be retrieved ONCE from the original clause, and the resulting hypothesis template must be frozen before calling `explain_instance`. All perturbed texts must use the same fixed hypothesis.

**Why:** If the predict_fn calls the full RAG+NLI pipeline per perturbation, each perturbed text retrieves different evidence, changing the hypothesis template. LIME then attributes word importance to a moving target — the explanations don't reflect classifier sensitivity to input words, they reflect RAG retrieval instability.

**How to apply:**
1. Before LIME, retrieve top evidence for the original clause: `evidence = rag.get_evidence(clause, law, top_k=1)`
2. Build a fixed hypothesis: `frozen_hyp = "This policy clause {} (Relevant requirement: " + evidence[0]["requirement"][:200] + ")"`
3. Pass this string into the predict_fn closure; the predict_fn calls the NLI classifier with this fixed hypothesis for all perturbations — no RAG calls inside.

See `compliance_app/explainer.py` `_make_predict_fn(law, frozen_hypothesis_template)`.
