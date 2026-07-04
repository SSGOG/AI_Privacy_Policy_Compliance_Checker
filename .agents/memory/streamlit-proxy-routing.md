---
name: Streamlit Proxy Routing in Replit
description: How to expose a Streamlit app via Replit's path proxy — non-artifact workflows don't get routing
---

**Rule:** A Streamlit app started via `configureWorkflow` with `outputType: "webview"` does NOT get a proxy route at any path. Users will see 404. To serve Streamlit at a path, you must register it as an artifact.

**Why:** Replit's shared proxy only routes to services declared in `artifact.toml` with `[[services]] paths = ["/..."]`. Non-artifact webview workflows have no path entry and are invisible through the proxy.

**How to apply:**
1. `createArtifact({ artifactType: "react-vite", slug: "...", previewPath: "/", title: "..." })` — note the allocated `ports.web` value.
2. Write a temp `artifact.edit.toml` replacing only the `[services.development] run` field with the Streamlit command, using absolute paths (the workflow runs from the artifact dir, not workspace root):
   ```
   run = "cd /home/runner/workspace/compliance_app && STREAMLIT_BROWSER_GATHER_USAGE_STATS=false python3 -m streamlit run app.py --server.port $PORT --server.headless true --server.address 0.0.0.0"
   ```
3. Remove the production `[services.production]` block — Streamlit has no static build.
4. Call `verifyAndReplaceArtifactToml(...)` to apply.
5. `WorkflowsRestart` the managed artifact workflow.

**Gotcha:** The workflow `run` command executes from the artifact directory (`artifacts/<slug>/`), so `cd compliance_app` will fail — always use the absolute path `/home/runner/workspace/compliance_app`.
