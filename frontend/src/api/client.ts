import type { PDEProblem, SolutionResponse } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function solveProblem(problem: PDEProblem): Promise<SolutionResponse> {
  const r = await fetch(`${BASE_URL}/solve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(problem),
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
