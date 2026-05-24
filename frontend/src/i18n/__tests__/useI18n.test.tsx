import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { I18nProvider, useI18n } from "../useI18n";

function HeaderHarness() {
  const { lang, setLang, t } = useI18n();
  return (
    <div>
      <span data-testid="title">{t("app.title")}</span>
      <span data-testid="current-lang">{lang}</span>
      <button onClick={() => setLang(lang === "es" ? "en" : "es")}>
        toggle
      </button>
    </div>
  );
}

describe("I18nProvider + useI18n", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("provides translations to children", () => {
    render(
      <I18nProvider>
        <HeaderHarness />
      </I18nProvider>,
    );
    // Spanish is the default unless the browser locale forces English.
    const title = screen.getByTestId("title").textContent ?? "";
    expect(title).toMatch(/PDESolver/);
  });

  it("toggles the language and re-renders translations", () => {
    render(
      <I18nProvider>
        <HeaderHarness />
      </I18nProvider>,
    );

    const initial = screen.getByTestId("current-lang").textContent;
    fireEvent.click(screen.getByText("toggle"));
    const next = screen.getByTestId("current-lang").textContent;
    expect(next).not.toBe(initial);
    expect(["es", "en"]).toContain(next);

    // The title also updated.
    const title = screen.getByTestId("title").textContent ?? "";
    if (next === "en") {
      expect(title).toMatch(/Pedagogical/);
    } else {
      expect(title).toMatch(/Pedagógico/);
    }
  });

  it("throws a clear error when used outside the provider", () => {
    // Silence the React console.error for the expected throw.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<HeaderHarness />)).toThrow(
      /useI18n must be used inside/i,
    );
    spy.mockRestore();
  });
});

import { vi } from "vitest";
