import { useState } from "react";
import { Library } from "./pages/Library";
import { Solve } from "./pages/Solve";
import { useTheme } from "./theme/useTheme";

type Tab = "write" | "natural" | "image" | "library";

export default function App() {
  const { theme, toggle } = useTheme();
  const [tab, setTab] = useState<Tab>("write");

  return (
    <div className={`app theme-${theme}`}>
      <header className="app-header">
        <div className="brand">
          <h1>PDESolver Pedagógico</h1>
          <p className="tagline">
            Un tutor que muestra cada paso, no una calculadora que devuelve el
            resultado.
          </p>
        </div>
        <button
          className="theme-toggle"
          onClick={toggle}
          aria-label="Cambiar tema"
        >
          {theme === "dark" ? "☼" : "☾"}
        </button>
      </header>

      <nav className="tabs" aria-label="Modo de entrada">
        <button
          className={`tab ${tab === "write" ? "tab-active" : ""}`}
          onClick={() => setTab("write")}
        >
          Escribir
        </button>
        <button
          className={`tab ${tab === "natural" ? "tab-active" : ""}`}
          onClick={() => setTab("natural")}
        >
          Lenguaje natural
        </button>
        <button
          className={`tab ${tab === "image" ? "tab-active" : ""}`}
          onClick={() => setTab("image")}
          title="Sube una foto de un problema"
        >
          Subir foto
        </button>
        <button
          className={`tab ${tab === "library" ? "tab-active" : ""}`}
          onClick={() => setTab("library")}
          style={{ marginLeft: "auto" }}
        >
          Biblioteca
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
        <small>
          Fase 5 — biblioteca local + exportación a PDF disponibles. Resuelve
          un problema, guárdalo en la biblioteca o expórtalo como PDF para
          estudio.
        </small>
      </footer>
    </div>
  );
}
