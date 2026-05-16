/** API client for the labor cost estimator backend. */

const BASE = "http://localhost:8000";

export interface QueryHit {
  id: string;
  model: string;
  code: string;
  qty_count: number;
  qty_median: number;
  qty_mean: number;
  confidence_range: {
    p10: number;
    p25: number;
    median: number;
    p75: number;
    p90: number;
  };
  price_mean: number;
  departments: string;
  franchises: string;
  similarity: number;
  document: string;
  compound: boolean;
  compound_max_ops: number;
  compound_pct: number;
  weighted_qty_p50: number;
  weighted_qty_p90: number;
}

export interface QueryResult {
  query: string;
  query_language: string;
  hits: QueryHit[];
  confidence_range: {
    p10: number;
    p50: number;
    p90: number;
  };
  outliers: { model: string; anomalies: { value: number; mean: number; sigma: number; deviation: number }[] }[];
  mode: string;
  natural_response?: string;
}

export interface HealthResponse {
  status: string;
  mode: string;
  local_llm_backend: string;
  embedding_model: string;
  force_local: boolean;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/health");
}

export async function searchQuery(params: {
  q: string;
  n?: number;
  department?: string;
  generate?: boolean;
  lang?: string;
}): Promise<QueryResult> {
  const sp = new URLSearchParams({ q: params.q });
  if (params.n) sp.set("n", String(params.n));
  if (params.department) sp.set("department", params.department);
  if (params.generate) sp.set("generate", "true");
  if (params.lang) sp.set("lang", params.lang);

  return apiFetch<QueryResult>(`/api/query?${sp.toString()}`, { method: "POST" });
}

// --- Dictionary API ---

export interface DictTerm {
  id: string;
  arabic_term: string;
  standard_category: string;
  english_term: string;
  created_at?: string;
}

export interface PendingTerm {
  id: string;
  term_text: string;
  query_text: string;
  status: string;
  created_at?: string;
}

export async function fetchTerms(search?: string, category?: string): Promise<{ terms: DictTerm[]; count: number }> {
  const sp = new URLSearchParams();
  if (search) sp.set("search", search);
  if (category) sp.set("category", category);
  const qs = sp.toString();
  return apiFetch(`/api/dictionary${qs ? "?" + qs : ""}`);
}

export async function createTerm(data: { arabic_term: string; standard_category: string; english_term?: string }): Promise<DictTerm> {
  return apiFetch("/api/dictionary", { method: "POST", body: JSON.stringify(data) });
}

export async function updateTerm(id: string, data: { arabic_term?: string; standard_category?: string; english_term?: string }): Promise<DictTerm> {
  return apiFetch(`/api/dictionary/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteTerm(id: string): Promise<void> {
  await apiFetch(`/api/dictionary/${id}`, { method: "DELETE" });
}

export async function fetchPending(): Promise<{ pending: PendingTerm[]; count: number }> {
  return apiFetch("/api/dictionary/pending");
}

export async function resolvePending(id: string, data: { arabic_term: string; standard_category: string; english_term?: string }): Promise<{ resolved_term_id: string }> {
  return apiFetch(`/api/dictionary/pending/${id}/resolve`, { method: "POST", body: JSON.stringify(data) });
}

// --- Settings ---

export async function setMode(forceLocal: boolean): Promise<{ mode: string; force_local: boolean }> {
  return apiFetch("/api/settings/mode", { method: "POST", body: JSON.stringify({ force_local: forceLocal }) });
}
