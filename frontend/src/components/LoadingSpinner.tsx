/**
 * Small CSS-only spinner with an optional pedagogical hint.
 *
 * The hint rotates through encouraging messages — the solve can take
 * several seconds for complex SOV problems and feels less awkward
 * when the UI says something concrete about what's happening.
 */
import { useEffect, useState } from "react";

const HINTS = [
  "Clasificando la EDP por discriminante…",
  "Examinando los tres casos de λ…",
  "Construyendo los modos normales…",
  "Aplicando ortogonalidad para extraer los coeficientes…",
  "Verificando la EDP, BCs e ICs…",
  "Componiendo la observación didáctica…",
  "Renderizando la superficie u(x, t)…",
];

interface Props {
  /** When provided, shows a rotating "what's happening" hint. */
  showHint?: boolean;
  /** Optional inline label next to the spinner. */
  label?: string;
}

export function LoadingSpinner({ showHint = false, label }: Props) {
  const [hintIdx, setHintIdx] = useState(0);

  useEffect(() => {
    if (!showHint) return;
    const id = window.setInterval(() => {
      setHintIdx((i) => (i + 1) % HINTS.length);
    }, 1800);
    return () => window.clearInterval(id);
  }, [showHint]);

  return (
    <div
      className="loading-spinner-wrap"
      role="status"
      aria-live="polite"
      aria-label={label ?? "Cargando"}
    >
      <span className="loading-spinner" aria-hidden="true" />
      {label && <span className="loading-spinner-label">{label}</span>}
      {showHint && (
        <span className="loading-spinner-hint">{HINTS[hintIdx]}</span>
      )}
    </div>
  );
}
