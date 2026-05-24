/**
 * Tiny i18n for UI chrome (buttons, headers, tab labels).
 *
 * The pedagogical content (step titles, explanations, observations,
 * formulas) is intentionally *not* translated — it lives in the
 * backend's Spanish templates and is the primary teaching language
 * the project is designed around. The natural-language parser already
 * accepts English ("heat equation on a bar of length L …"), so the
 * cross-language user is mostly served. This module covers the UI
 * chrome that surrounds the pedagogy.
 *
 * No external dependencies — a dictionary lookup with a fallback to
 * Spanish is enough. The chosen language is persisted to localStorage.
 */

export type Lang = "es" | "en";

export const SUPPORTED_LANGS: Lang[] = ["es", "en"];

// Each key holds the same string in both languages. The Spanish entry
// is the source of truth; English is a courtesy translation.
export const messages = {
  // Header / tagline
  "app.title": {
    es: "PDESolver Pedagógico",
    en: "Pedagogical PDESolver",
  },
  "app.tagline": {
    es: "Un tutor que muestra cada paso, no una calculadora que devuelve el resultado.",
    en: "A tutor that shows every step, not a calculator that returns an answer.",
  },
  "app.themeToggle.aria": {
    es: "Cambiar tema",
    en: "Toggle theme",
  },
  "app.langToggle.aria": {
    es: "Cambiar idioma",
    en: "Switch language",
  },
  "app.footer": {
    es: "Resuelve un problema, guárdalo en la biblioteca o expórtalo como PDF para estudio.",
    en: "Solve a problem, save it to your library or export as PDF for study.",
  },

  // Tabs
  "tabs.label": {
    es: "Modo de entrada",
    en: "Input mode",
  },
  "tabs.write": {
    es: "Escribir",
    en: "Write",
  },
  "tabs.natural": {
    es: "Lenguaje natural",
    en: "Natural language",
  },
  "tabs.image": {
    es: "Subir foto",
    en: "Upload photo",
  },
  "tabs.image.title": {
    es: "Sube una foto de un problema",
    en: "Upload a photo of a problem",
  },
  "tabs.library": {
    es: "Biblioteca",
    en: "Library",
  },

  // Solve panel — chrome only.
  "solve.preview": {
    es: "Vista previa",
    en: "Preview",
  },
  "solve.preview.empty.write": {
    es: "Configura el problema a la izquierda y pulsa Resolver. Verás la solución, la superficie u(x, t) y la convergencia.",
    en: "Configure the problem on the left and press Solve. You will see the solution, the u(x, t) surface and the convergence.",
  },
  "solve.preview.empty.natural": {
    es: "Describe el problema a la izquierda y pulsa Interpretar. Después podrás confirmar la interpretación antes de resolver.",
    en: "Describe the problem on the left and press Interpret. You will then confirm the interpretation before solving.",
  },
  "solve.preview.empty.image": {
    es: "Sube una foto del problema. Verás la imagen y la transcripción lado a lado para confirmar antes de resolver.",
    en: "Upload a photo of the problem. You'll see the image and the transcription side-by-side to confirm before solving.",
  },
  "solve.loading": {
    es: "Resolviendo el problema…",
    en: "Solving the problem…",
  },
  "solve.error": {
    es: "Error al resolver:",
    en: "Solve error:",
  },
  "solve.error.close": {
    es: "Cerrar",
    en: "Dismiss",
  },
  "solve.solution.label": {
    es: "Solución final",
    en: "Final solution",
  },
  "solve.steps.heading": {
    es: "Desarrollo paso a paso",
    en: "Step-by-step development",
  },

  // Buttons
  "btn.solve": {
    es: "Resolver con explicación detallada",
    en: "Solve with detailed explanation",
  },
  "btn.solving": {
    es: "Resolviendo…",
    en: "Solving…",
  },
  "btn.saveLibrary": {
    es: "Guardar en biblioteca",
    en: "Save to library",
  },
  "btn.saving": {
    es: "Guardando…",
    en: "Saving…",
  },
  "btn.saved": {
    es: "Guardado ✓",
    en: "Saved ✓",
  },
  "btn.exportPdf": {
    es: "Exportar a PDF",
    en: "Export to PDF",
  },
} as const satisfies Record<string, Record<Lang, string>>;

export type MessageKey = keyof typeof messages;

const STORAGE_KEY = "pdesolver.lang";

export function loadInitialLang(): Lang {
  if (typeof window === "undefined") return "es";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "es" || stored === "en") return stored;
  // Best-effort detection from the browser.
  const browser = window.navigator?.language?.slice(0, 2);
  return browser === "en" ? "en" : "es";
}

export function persistLang(lang: Lang): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, lang);
}

export function t(key: MessageKey, lang: Lang): string {
  return messages[key]?.[lang] ?? messages[key]?.es ?? String(key);
}
