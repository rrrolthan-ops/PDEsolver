import { useState } from "react";
import { useI18n } from "./i18n/useI18n";
import { Library } from "./pages/Library";
import { Solve } from "./pages/Solve";
import { useTheme } from "./theme/useTheme";

type Tab = "write" | "natural" | "image" | "library";

export default function App() {
  const { theme, toggle } = useTheme();
  const { t, lang, setLang } = useI18n();
  const [tab, setTab] = useState<Tab>("write");

  return (
    <div className={`app theme-${theme}`}>
      <header className="app-header">
        <div className="brand">
          <h1>{t("app.title")}</h1>
          <p className="tagline">{t("app.tagline")}</p>
        </div>
        <div className="header-actions">
          <button
            className="lang-toggle"
            onClick={() => setLang(lang === "es" ? "en" : "es")}
            aria-label={t("app.langToggle.aria")}
            title={t("app.langToggle.aria")}
          >
            {lang === "es" ? "EN" : "ES"}
          </button>
          <button
            className="theme-toggle"
            onClick={toggle}
            aria-label={t("app.themeToggle.aria")}
          >
            {theme === "dark" ? "☼" : "☾"}
          </button>
        </div>
      </header>

      <nav className="tabs" aria-label={t("tabs.label")}>
        <button
          className={`tab ${tab === "write" ? "tab-active" : ""}`}
          onClick={() => setTab("write")}
        >
          {t("tabs.write")}
        </button>
        <button
          className={`tab ${tab === "natural" ? "tab-active" : ""}`}
          onClick={() => setTab("natural")}
        >
          {t("tabs.natural")}
        </button>
        <button
          className={`tab ${tab === "image" ? "tab-active" : ""}`}
          onClick={() => setTab("image")}
          title={t("tabs.image.title")}
        >
          {t("tabs.image")}
        </button>
        <button
          className={`tab ${tab === "library" ? "tab-active" : ""}`}
          onClick={() => setTab("library")}
          style={{ marginLeft: "auto" }}
        >
          {t("tabs.library")}
        </button>
      </nav>

      <main className="app-main">
        {tab === "library" ? (
          <Library />
        ) : (
          <Solve mode={tab as "write" | "natural" | "image"} />
        )}
      </main>

      <footer className="app-footer">
        <small>{t("app.footer")}</small>
      </footer>
    </div>
  );
}
