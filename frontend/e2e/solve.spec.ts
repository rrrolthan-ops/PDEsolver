/**
 * End-to-end smoke test for the Solve flow.
 *
 * Validates the happy path: the default heat-equation problem is solved
 * successfully via the live backend, step cards render, and KaTeX math
 * appears in the result. This is the single most valuable E2E check —
 * if it passes, the entire stack (parser → solver → API → frontend → KaTeX)
 * is wired correctly.
 */
import { test, expect } from "@playwright/test";

test("solves the default heat problem and renders the step list", async ({
  page,
}) => {
  await page.goto("/");

  // Header and tabs are visible.
  await expect(page.getByRole("heading", { name: /pdesolver/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /escribir|write/i })).toBeVisible();

  // The "Resolver" / "Solve" button exists on the manual editor tab.
  const solveButton = page.getByRole("button", {
    name: /resolver con explicación|solve with detailed/i,
  });
  await expect(solveButton).toBeVisible();

  // Click it. The backend's heat-1D SOV solver runs.
  await solveButton.click();

  // Loading skeleton appears, then the solution. Wait for the step list.
  // Allow up to 30s — the backend can be cold on first run.
  await expect(
    page.getByRole("heading", {
      name: /desarrollo paso a paso|step-by-step development/i,
    }),
  ).toBeVisible({ timeout: 30_000 });

  // At least the "Planteamiento" (statement) step should appear.
  await expect(
    page.getByRole("heading", { name: /paso 0/i }),
  ).toBeVisible();

  // KaTeX rendered math: there must be at least one .katex node.
  await expect(page.locator(".katex").first()).toBeVisible();
});

test("language toggle switches the UI to English", async ({ page }) => {
  await page.goto("/");

  // Default Spanish: the tagline ends with "calculadora que devuelve el resultado."
  await expect(page.getByText(/calculadora que devuelve/i)).toBeVisible();

  // Click the EN toggle.
  await page.getByRole("button", { name: /switch language|cambiar idioma/i }).click();

  // English tagline ends with "calculator that returns an answer."
  await expect(
    page.getByText(/calculator that returns an answer/i),
  ).toBeVisible();

  // The toggle now reads "ES" (i.e. would switch back to Spanish).
  await expect(page.getByRole("button", { name: /switch language|cambiar idioma/i }))
    .toContainText("ES");
});

test("library tab loads without errors", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /biblioteca|library/i }).click();

  // The page should not blow up; some heading or empty-state message
  // should be visible.
  await expect(page.locator("main")).toBeVisible();
});
