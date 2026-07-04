"""
Start the FastAPI backend server.
Run: python main.py
Or:  uvicorn compliance_app.api:app --host 0.0.0.0 --port 8000 --reload
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "compliance_app"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", os.environ.get("API_PORT", 8000)))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
