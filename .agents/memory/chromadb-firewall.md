---
name: ChromaDB Firewall Pin
description: chromadb>=1.0 is blocked by Replit's package firewall; pin to <1.0
---

**Rule:** Always install `chromadb<1.0` in this environment. Latest chromadb (1.5.x) returns HTTP 403 from the Replit package firewall.

**Why:** Replit's package firewall blocks the chromadb 1.5.x wheel. Version 0.6.3 installed and works.

**How to apply:** In requirements.txt and install commands, always use `chromadb<1.0`. The 0.6.x API (`PersistentClient`, `create_collection`, `query(include=["metadatas","distances"])`) is fully compatible with the code in `compliance_app/rag_pipeline.py`.
