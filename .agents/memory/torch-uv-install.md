---
name: Torch/Transformers uv Install Failure
description: uv resolver fails for torch, transformers, sentence-transformers on Linux due to Python 3.14 resolution; use pip directly
---

**Rule:** Do NOT use `installLanguagePackages` for torch, transformers, sentence-transformers, huggingface-hub, or accelerate. Use `python3 -m pip install` directly.

**Why:** The uv resolver in this workspace tries to resolve for `python_full_version >= '3.14' and sys_platform == 'linux'`, and those packages have no wheels for Python 3.14 yet. Even with `requires-python = ">=3.11,<3.14"` in pyproject.toml the resolver still fails.

**How to apply:**
- `python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu`
- `python3 -m pip install transformers tokenizers sentence-transformers`
- `installLanguagePackages` works fine for: streamlit, pandas, numpy, scikit-learn, plotly, fpdf2, lime, shap, pypdf, chromadb<1.0
