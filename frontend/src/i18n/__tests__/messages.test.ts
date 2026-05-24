import { describe, it, expect, beforeEach } from "vitest";
import { messages, t, loadInitialLang, persistLang } from "../messages";

describe("i18n messages", () => {
  it("has both es and en entries for every key", () => {
    for (const [key, entry] of Object.entries(messages)) {
      expect(entry.es, `missing es for ${key}`).toBeTruthy();
      expect(entry.en, `missing en for ${key}`).toBeTruthy();
    }
  });

  it("returns the requested language's translation", () => {
    expect(t("tabs.write", "es")).toBe("Escribir");
    expect(t("tabs.write", "en")).toBe("Write");
  });

  it("falls back to Spanish when an unknown lang is forced", () => {
    // @ts-expect-error — intentionally forcing an unsupported lang.
    expect(t("tabs.write", "fr")).toBe("Escribir");
  });

  it("never returns undefined for a known key", () => {
    for (const key of Object.keys(messages)) {
      const esVal = t(key as keyof typeof messages, "es");
      const enVal = t(key as keyof typeof messages, "en");
      expect(esVal).toBeTruthy();
      expect(enVal).toBeTruthy();
    }
  });
});

describe("i18n persistence", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("loadInitialLang falls back to browser locale when localStorage is empty", () => {
    const got = loadInitialLang();
    expect(["es", "en"]).toContain(got);
  });

  it("persistLang round-trips through localStorage", () => {
    persistLang("en");
    expect(window.localStorage.getItem("pdesolver.lang")).toBe("en");
    expect(loadInitialLang()).toBe("en");

    persistLang("es");
    expect(loadInitialLang()).toBe("es");
  });
});
