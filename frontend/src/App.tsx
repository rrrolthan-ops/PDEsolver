import { useState } from "react";
import { Solve } from "./pages/Solve";
import { useTheme } from "./theme/useTheme";

export default function App() {
  const { theme, toggle } = useTheme();
  const [tab] = useState<"write" | "natural" | "image">("write");

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
        <button className="tab tab-active" disabled>
          Escribir
        </button>
        <button className="tab tab-disabled" disabled title="Disponible en Fase 3">
          Lenguaje natural
        </button>
        <button className="tab tab-disabled" disabled title="Disponible en Fase 4">
          Subir foto / PDF
        </button>
      </nav>

      <main className="app-main">
        {tab === "write" && <Solve />}
      </main>

      <footer className="app-footer">
        <small>
          Fase 1 — ecuación del calor 1D por separación de variables. Otras
          EDPs y métodos llegan en fases posteriores.
        </small>
      </footer>
    </div>
  );
}
