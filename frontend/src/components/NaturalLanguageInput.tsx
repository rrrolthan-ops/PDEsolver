import { useState } from "react";
import { parseNaturalLanguage } from "../api/client";
import type { PDEProblem } from "../api/types";

interface Props {
  onParsed: (problem: PDEProblem, source: string, notes: string | null) => void;
}

const EXAMPLES = [
  "Resuelve la ecuación del calor en una barra de longitud L con extremos a temperatura cero y perfil inicial f(x) = sin(pi*x/L).",
  "Cuerda fija de longitud L con perfil inicial f(x) = sin(pi*x/L) y velocidad inicial cero.",
  "Ecuación de onda en la recta entera con condición inicial f(x) = exp(-x^2).",
  "Laplace en un disco de radio R con dato en el borde cos(theta).",
  "Tambor circular de radio R que vibra con perfil inicial 1 - (r/R)^2.",
  "Partícula en un pozo infinito unidimensional de longitud L.",
];

/**
 * Natural-language input panel.
 *
 * The user types a free-text description; we POST it to /parse_natural
 * and pass the resulting PDEProblem up to the parent, which then shows
 * a confirmation view. The LLM never solves — it only classifies.
 */
export function NaturalLanguageInput({ onParsed }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleParse = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await parseNaturalLanguage(text);
      onParsed(resp.problem, resp.source, resp.notes);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <h2>Lenguaje natural</h2>
      <p style={{ marginTop: 0, color: "var(--text-muted)", fontSize: 14 }}>
        Describe el problema en español o inglés. El sistema lo
        traducirá a la representación canónica y te lo mostrará
        para que lo confirmes antes de resolver.
      </p>

      <label className="field">
        <span className="field-label">Descripción del problema</span>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          placeholder={EXAMPLES[0]}
          spellCheck={false}
        />
      </label>

      <div style={{ marginBottom: 12 }}>
        <span className="field-label">Ejemplos rápidos:</span>
        <ul style={{ marginTop: 6, paddingLeft: 18, fontSize: 13 }}>
          {EXAMPLES.map((ex, i) => (
            <li key={i} style={{ marginBottom: 4 }}>
              <button
                type="button"
                onClick={() => setText(ex)}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--accent)",
                  cursor: "pointer",
                  textAlign: "left",
                  padding: 0,
                  fontSize: "inherit",
                  fontFamily: "inherit",
                  textDecoration: "underline",
                }}
              >
                {ex}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <button
        className="solve-button"
        onClick={handleParse}
        disabled={loading || !text.trim()}
      >
        {loading ? "Interpretando…" : "Interpretar"}
      </button>

      {error && (
        <div className="error-banner" role="alert" style={{ marginTop: 12 }}>
          <strong>No pude interpretar:</strong> {error}
        </div>
      )}

      <p style={{ marginTop: 12, fontSize: 12, color: "var(--text-muted)" }}>
        El LLM se usa <strong>sólo como clasificador semántico</strong>. La
        resolución matemática siempre la hace el motor simbólico determinista.
        Tu interpretación pasará por una vista de confirmación antes de
        resolverse.
      </p>
    </section>
  );
}
