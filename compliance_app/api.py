"""
FastAPI backend for the AI Privacy Compliance Checker.
"""

from __future__ import annotations

import os
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
import jwt

import service

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "24"))

# Default admin credentials (used as fallback if no users file exists)
DEFAULT_USERNAME = os.environ.get("AUTH_USERNAME", "admin")
DEFAULT_PASSWORD = os.environ.get("AUTH_PASSWORD", "admin123")

# Simple file-based user store
USERS_FILE = os.environ.get("USERS_FILE", "./users.json")


def _load_users() -> dict[str, str]:
    """Load users from JSON file. Returns {username: password}."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Seed with default admin
    users = {DEFAULT_USERNAME: DEFAULT_PASSWORD}
    _save_users(users)
    return users


def _save_users(users: dict[str, str]) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


app = FastAPI(title="AI Privacy Compliance Checker API", version="1.0.0")
security = HTTPBearer(auto_error=False)

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6)


class LoginResponse(BaseModel):
    token: str
    expires_at: str


class SampleAnalyzeRequest(BaseModel):
    clause: str = Field(min_length=10)
    laws: list[str] = Field(default_factory=lambda: ["GDPR"])
    top_k_evidence: int = Field(default=3, ge=1, le=5)


class ExplainRequest(BaseModel):
    clause: str = Field(min_length=10)
    law: str
    result: dict[str, Any]


class ReportRequest(BaseModel):
    policy_name: str = "Privacy Policy"
    clauses: list[str]
    results_by_law: dict[str, list[dict[str, Any]]]


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def create_token(username: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expires, "iat": datetime.now(timezone.utc)}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires


def verify_token(credentials: HTTPAuthorizationCredentials | None = Security(HTTPBearer(auto_error=False))) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


AuthUser = Annotated[str, Depends(verify_token)]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup() -> None:
    _load_users()  # ensure users file is initialised
    if JWT_SECRET == "change-me-in-production":
        print("WARNING: Using default JWT_SECRET. Set JWT_SECRET in your environment.")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    users = _load_users()
    stored = users.get(body.username)
    if stored is None or not secrets.compare_digest(stored, body.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, expires = create_token(body.username)
    return LoginResponse(token=token, expires_at=expires.isoformat())


@app.post("/api/auth/signup", response_model=LoginResponse)
def signup(body: SignupRequest) -> LoginResponse:
    users = _load_users()
    if body.username in users:
        raise HTTPException(status_code=409, detail="Username already exists")
    users[body.username] = body.password
    _save_users(users)
    token, expires = create_token(body.username)
    return LoginResponse(token=token, expires_at=expires.isoformat())


@app.post("/api/analyze/upload")
async def analyze_upload(
    file: UploadFile = File(...),
    laws: str = Form(default="GDPR"),
    top_k_evidence: int = Form(default=3),
    _user: str = Depends(verify_token),
) -> dict[str, Any]:
    selected_laws = [law.strip() for law in laws.split(",") if law.strip()]
    if not selected_laws:
        raise HTTPException(status_code=400, detail="Select at least one regulation.")
    if top_k_evidence < 1 or top_k_evidence > 5:
        raise HTTPException(status_code=400, detail="Evidence count must be between 1 and 5.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        policy_name, clauses = service.parse_document(file.filename or "policy.txt", raw_bytes)
        results_by_law = service.analyze_clauses(clauses, selected_laws, top_k_evidence)
        return service.build_analysis_response(policy_name, clauses, results_by_law)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@app.post("/api/analyze/sample")
def analyze_sample(body: SampleAnalyzeRequest, _user: str = Depends(verify_token)) -> dict[str, Any]:
    if not body.laws:
        raise HTTPException(status_code=400, detail="Select at least one regulation.")
    try:
        results = service.analyze_sample_clause(body.clause, body.laws, body.top_k_evidence)
        return {"clause": body.clause, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@app.post("/api/explain")
def explain(body: ExplainRequest, _user: str = Depends(verify_token)) -> dict[str, Any]:
    try:
        return service.explain_clause(body.clause, body.law, body.result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Explanation unavailable: {exc}") from exc


@app.post("/api/reports/csv")
def report_csv(body: ReportRequest, _user: str = Depends(verify_token)) -> Response:
    csv_bytes = service.generate_csv(body.clauses, body.results_by_law, body.policy_name)
    filename = f"compliance_report_{body.policy_name.replace(' ', '_')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/reports/pdf")
def report_pdf(body: ReportRequest, _user: str = Depends(verify_token)) -> Response:
    try:
        pdf_bytes = service.generate_pdf(body.clauses, body.results_by_law, body.policy_name)
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    filename = f"compliance_report_{body.policy_name.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
