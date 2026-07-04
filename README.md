# AI Privacy Compliance Checker

Your intelligent assistant for GDPR & CCPA data protection compliance.

## Project Structure

```
compliance_app/     ← Python FastAPI backend
artifacts/compliance-checker/  ← React + Vite frontend
```

---

## Setup

### 1. Backend (Python)

```bash
cd compliance_app
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required credentials you must set in `.env`:**

| Variable | Description |
|---|---|
| `AUTH_USERNAME` | Login username (default: `admin`) |
| `AUTH_PASSWORD` | Login password — **change this** |
| `JWT_SECRET` | Long random secret for JWT signing — **change this** |

Start the API server:

```bash
cd ..
python main.py
# or: uvicorn compliance_app.api:app --host 0.0.0.0 --port 8000 --reload
```

The API runs at `http://localhost:8000`.

---

### 2. Frontend (React)

```bash
cd artifacts/compliance-checker
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

Set `VITE_API_URL` in a `.env.local` file if your backend runs on a different URL:

```
VITE_API_URL=http://localhost:8000
```

---

## Usage

1. Open `http://localhost:5173`
2. Click **Get Started** → **Sign In** with your credentials
3. Upload a privacy policy PDF or TXT, or paste a sample clause
4. Select GDPR and/or CCPA regulations
5. View clause-by-clause results, legal evidence, and LIME explanations
6. Download CSV or PDF report

---

## Notes

- First run downloads AI models (~500 MB). Subsequent runs use the cache.
- This is a **research tool** — not legal advice.
