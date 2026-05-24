import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { StepCard } from "../StepCard";
import type { Step } from "../../api/types";

const makeStep = (overrides: Partial<Step> = {}): Step => ({
  kind: "statement",
  title: "Paso 0 — Planteamiento",
  explanation_md: "Texto de la explicación.",
  latex: "u_t = \\alpha^2 u_{xx}",
  sympy_repr: null,
  observations: [],
  level: "basic",
  ...overrides,
});

describe("StepCard", () => {
  it("renders the title and the kind tag (Spanish label)", () => {
    render(<StepCard step={makeStep()} />);
    expect(screen.getByText("Paso 0 — Planteamiento")).toBeInTheDocument();
    expect(screen.getByText("Planteamiento")).toBeInTheDocument();
  });

  it("renders the explanation Markdown content", () => {
    render(<StepCard step={makeStep({ explanation_md: "Hola **mundo**." })} />);
    // react-markdown wraps text in a <p>; the bold word is inside <strong>.
    expect(screen.getByText("mundo")).toBeInTheDocument();
  });

  it("expands by default and collapses on header click", () => {
    render(<StepCard step={makeStep()} />);
    // Body visible initially.
    expect(screen.getByText("Texto de la explicación.")).toBeInTheDocument();
    // Clicking the header collapses.
    fireEvent.click(screen.getByText("Paso 0 — Planteamiento"));
    expect(screen.queryByText("Texto de la explicación.")).toBeNull();
  });

  it("renders each observation with its labelled prefix", () => {
    const step = makeStep({
      observations: [
        { kind: "pitfall", text_md: "Cuidado con esto." },
        { kind: "theorem", text_md: "Teorema importante." },
      ],
    });
    render(<StepCard step={step} />);
    expect(screen.getByText("Atención:")).toBeInTheDocument();
    expect(screen.getByText("Teorema:")).toBeInTheDocument();
    expect(screen.getByText("Cuidado con esto.")).toBeInTheDocument();
    expect(screen.getByText("Teorema importante.")).toBeInTheDocument();
  });

  it("falls back to the raw kind when not in the Spanish dictionary", () => {
    // Cast to bypass the StepKind union for the failure-mode test.
    const step = makeStep({ kind: "unknown_kind" as Step["kind"] });
    render(<StepCard step={step} />);
    expect(screen.getByText("unknown_kind")).toBeInTheDocument();
  });

  it("does not render observations when the array is empty", () => {
    render(<StepCard step={makeStep({ observations: [] })} />);
    expect(screen.queryByRole("note")).toBeNull();
  });
});
