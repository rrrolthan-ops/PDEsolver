import { useState } from "react";
import { Solve } from "./pages/Solve";
import { useTheme } from "./theme/useTheme";

type InputMode = "write" | "natural" | "image";

export default function App() {
  const { theme, toggle } = useTheme();
  const [tab, setTab] = useState<InputMode>("write");

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
          className="tab tab-disabled"
          disabled
          title="Disponible en Fase 4"
        >
          Subir foto / PDF
        </button>
      </nav>

      <main className="app-main">
        {tab !== "image" && <Solve mode={tab as "write" | "natural"} />}
      </main>

      <footer className="app-footer">
        <small>
          Fase 3 — entrada en lenguaje natural disponible (clasificador
          determinista + Claude opcional como clasificador semántico). Fase 4
          (visión) en construcción.
        </small>
      </footer>
    </div>
  );
}
