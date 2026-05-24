/**
 * Vitest setup: jest-dom matchers + a couple of jsdom shims that the
 * production code needs (KaTeX checks window.matchMedia, Plotly probes
 * ResizeObserver, etc.).
 */
import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// JSDOM doesn't ship matchMedia by default.
if (!window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

// Plotly uses ResizeObserver; jsdom lacks it.
if (!("ResizeObserver" in window)) {
  // @ts-expect-error — assigning a minimal mock on the global.
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
