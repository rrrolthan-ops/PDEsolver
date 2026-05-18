import type { PDEProblem, SolutionResponse } from "./types";

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
