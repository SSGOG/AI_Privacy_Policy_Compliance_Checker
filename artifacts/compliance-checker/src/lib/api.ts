const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const TOKEN_KEY = 'compliance_auth_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (auth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return response.json() as Promise<T>;
  }

  return response as unknown as T;
}

export interface Evidence {
  article: string;
  title: string;
  text: string;
  requirement: string;
  similarity: number;
}

export interface ClauseResult {
  status: string;
  confidence: number;
  summary: string;
  scores: Record<string, number>;
  evidence: Evidence[];
}

export interface LawStats {
  total: number;
  compliant: number;
  partial: number;
  non_compliant: number;
  irrelevant: number;
  score: number;
}

export interface AnalysisResponse {
  policy_name: string;
  clauses: string[];
  results_by_law: Record<string, ClauseResult[]>;
  stats: Record<string, LawStats>;
}

export interface SampleAnalysisResponse {
  clause: string;
  results: Record<string, ClauseResult>;
}

export interface ExplainResponse {
  textual_summary: string;
  top_features: { word: string; weight: number }[];
  highlighted_text: string;
}

export async function login(username: string, password: string) {
  return apiFetch<{ token: string; expires_at: string }>(
    '/api/auth/login',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    },
    false,
  );
}

export async function signup(username: string, password: string) {
  return apiFetch<{ token: string; expires_at: string }>(
    '/api/auth/signup',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    },
    false,
  );
}

export async function analyzeUpload(
  file: File,
  laws: string[],
  topKEvidence: number,
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('laws', laws.join(','));
  formData.append('top_k_evidence', String(topKEvidence));

  return apiFetch<AnalysisResponse>('/api/analyze/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function analyzeSample(
  clause: string,
  laws: string[],
  topKEvidence: number,
): Promise<SampleAnalysisResponse> {
  return apiFetch<SampleAnalysisResponse>('/api/analyze/sample', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clause, laws, top_k_evidence: topKEvidence }),
  });
}

export async function explainClause(
  clause: string,
  law: string,
  result: ClauseResult,
): Promise<ExplainResponse> {
  return apiFetch<ExplainResponse>('/api/explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clause, law, result }),
  });
}

export async function downloadReport(
  format: 'csv' | 'pdf',
  payload: {
    policy_name: string;
    clauses: string[];
    results_by_law: Record<string, ClauseResult[]>;
  },
): Promise<Blob> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/reports/${format}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to download ${format.toUpperCase()} report`);
  }

  return response.blob();
}

export const STATUS_COLORS: Record<string, string> = {
  'Fully Compliant': '#2d9c4e',
  'Partially Compliant': '#e07b00',
  'Non-Compliant': '#c0392b',
  'Not Applicable': '#7f8c8d',
};
