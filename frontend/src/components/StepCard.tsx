import { useState } from "react";
import type { Step } from "../api/types";
import { KatexBlock } from "./KatexBlock";
import { Markdown } from "./Markdown";

interface Props {
  step: Step;
}

const KIND_LABEL: Record<string, string> = {
  statement: "Planteamiento",
  classification: "Clasificación",
  method_choice: "Elección de método",
  development: "Desarrollo",
  boundary: "Condiciones de contorno",
  initial: "Condición inicial",
  final: "Solución final",
  verification: "Verificación",
  visualization: "Visualización",
  interpretation: "Interpretación",
  observation: "Observación",
};

const OBS_LABEL: Record<string, string> = {
  pitfall: "Atención",
  intuition: "Intuición",
  theorem: "Teorema",
  alternative: "Alternativa",
};

export function StepCard({ step }: Props) {
  // Cards start expanded by design — the user explicitly asked for this.
  const [open, setOpen] = useState(true);

  return (
    <article className="step-card">
      <header className="step-header" onClick={() => setOpen(!open)}>
        <h3>{step.title}</h3>
        <span className="step-kind-tag">{KIND_LABEL[step.kind] ?? step.kind}</span>
      </header>
      {open && (
        <div className="step-body">
          {step.explanation_md && <Markdown source={step.explanation_md} />}
          {step.latex && <KatexBlock latex={step.latex} />}
          {step.observations.map((o, i) => (
            <div
              key={i}
              className={`observation observation-${o.kind}`}
              role="note"
            >
              <span className="obs-label">{OBS_LABEL[o.kind]}:</span>
              <Markdown source={o.text_md} />
            </div>
          ))}
        </div>
      )}
    </article>
  );
}
