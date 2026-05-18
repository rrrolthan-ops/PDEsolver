import type {
  LibraryItem,
  LibraryListItem,
  LibrarySaveRequest,
  PDEProblem,
  SolutionResponse,
  VisionExtractionResult,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface NaturalLanguageParseResponse {
  problem: PDEProblem;
  source: string; // "deterministic" | "llm:<model>"
  notes: string | null;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try {
      const errBody = await r.json();
      if (errBody?.detail) detail = errBody.detail;
    } catch {
      /* swallow */
    }
    throw new Error(detail);
  }
  return r.json();
}

export async function solveProblem(problem: PDEProblem): Promise<SolutionResponse> {
  return postJson<SolutionResponse>("/solve", problem);
}

export async function parseNaturalLanguage(
  text: string,
): Promise<NaturalLanguageParseResponse> {
  return postJson<NaturalLanguageParseResponse>("/parse_natural", { text });
}

export async function extractFromImage(
  file: File,
  hint?: string,
): Promise<VisionExtractionResult> {
  const form = new FormData();
  form.append("file", file);
  if (hint?.trim()) form.append("hint", hint.trim());
  const r = await fetch(`${BASE_URL}/vision/extract`, {
    method: "POST",
    body: form,
  });
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try {
      const body = await r.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* swallow */
    }
    throw new Error(detail);
  }
  return r.json();
}

// --- Library ----------------------------------------------------------

export async function saveLibraryEntry(
  body: LibrarySaveRequest,
): Promise<LibraryItem> {
  return postJson<LibraryItem>("/library", body);
}

export async function listLibrary(filter?: {
  equation_kind?: string;
}): Promise<LibraryListItem[]> {
  const params = new URLSearchParams();
  if (filter?.equation_kind) params.set("equation_kind", filter.equation_kind);
  const url = `${BASE_URL}/library${params.size ? "?" + params : ""}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function getLibraryEntry(id: string): Promise<LibraryItem> {
  const r = await fetch(`${BASE_URL}/library/${id}`);
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try {
      const body = await r.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* swallow */
    }
    throw new Error(detail);
  }
  return r.json();
}

export async function deleteLibraryEntry(id: string): Promise<void> {
  const r = await fetch(`${BASE_URL}/library/${id}`, { method: "DELETE" });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
}
