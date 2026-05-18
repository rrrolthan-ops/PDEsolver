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
          className={`tab ${tab === "image" ? "tab-active" : ""}`}
          onClick={() => setTab("image")}
          title="Sube una foto de un problema"
        >
          Subir foto
        </button>
      </nav>

      <main className="app-main">
        <Solve mode={tab} />
      </main>

      <footer className="app-footer">
        <small>
          Fase 4 — las tres modalidades de entrada (manual, lenguaje natural,
          imagen) están operativas. La extracción visual usa
          claude-haiku-4-5 como clasificador; la resolución matemática
          siempre es simbólica.
        </small>
      </footer>
    </div>
  );
}
