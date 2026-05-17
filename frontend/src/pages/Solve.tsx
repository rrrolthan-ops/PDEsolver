import { useState } from "react";
import { solveProblem } from "../api/client";
import type {
  BoundaryCondition,
  DetailLevel,
  InitialCondition,
  PDEProblem,
  SolutionResponse,
} from "../api/types";
import { DetailSlider, shouldShow } from "../components/DetailSlider";
import { HeatPlot } from "../components/HeatPlot";
import { LatexEditor } from "../components/LatexEditor";
import { StepCard } from "../components/StepCard";

const DEFAULT_PROBLEM: PDEProblem = {
  equation_latex: "u_t = alpha^2 * u_{xx}",
  equation_kind: "heat",
  domain: { x: ["0", "L"], t: ["0", "infty"] },
  boundary_conditions: [
    { type: "dirichlet", where: "x=0", value: "0" },
    { type: "dirichlet", where: "x=L", value: "0" },
  ],
  initial_conditions: [{ order: 0, value: "sin(pi*x/L)" }],
  parameters: { alpha: "positive", L: "positive" },
};

export function Solve() {
  const [equation, setEquation] = useState(DEFAULT_PROBLEM.equation_latex);
  const [xLow, setXLow] = useState("0");
  const [xHigh, setXHigh] = useState("L");
  const [bcLeft, setBcLeft] = useState("0");
  const [bcRight, setBcRight] = useState("0");
  const [initial, setInitial] = useState(
    DEFAULT_PROBLEM.initial_conditions[0].value,
  );
  const [detail, setDetail] = useState<DetailLevel>("exhaustive");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SolutionResponse | null>(null);

  const buildProblem = (): PDEProblem => {
    const bcs: BoundaryCondition[] = [
      { type: "dirichlet", where: `x=${xLow}`, value: bcLeft },
      { type: "dirichlet", where: `x=${xHigh}`, value: bcRight },
    ];
    const ics: InitialCondition[] = [{ order: 0, value: initial }];
    return {
      equation_latex: equation,
      equation_kind: "heat",
      domain: { x: [xLow, xHigh], t: ["0", "infty"] },
      boundary_conditions: bcs,
      initial_conditions: ics,
      parameters: { alpha: "positive", L: "positive" },
    };
  };

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await solveProblem(buildProblem());
      setResult(resp);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const visibleSteps = result?.steps.filter((s) => shouldShow(s.level, detail)) ?? [];

  return (
    <div>
      <div className="solve-grid">
        <section className="panel">
          <h2>Planteamiento del problema</h2>
          <LatexEditor
            label="EDP (usa notación física: u_t, u_xx, …)"
            value={equation}
            onChange={setEquation}
            rows={2}
          />

          <div className="bc-row">
            <label className="field">
              <span className="field-label">Dominio: x mínimo</span>
              <input
                value={xLow}
                onChange={(e) => setXLow(e.target.value)}
                spellCheck={false}
              />
            </label>
            <label className="field">
              <span className="field-label">Dominio: x máximo</span>
              <input
                value={xHigh}
                onChange={(e) => setXHigh(e.target.value)}
                spellCheck={false}
              />
            </label>
          </div>

          <div className="bc-row">
            <label className="field">
              <span className="field-label">
                Contorno en x = {xLow}
              </span>
              <input
                value={bcLeft}
                onChange={(e) => setBcLeft(e.target.value)}
                spellCheck={false}
              />
            </label>
            <label className="field">
              <span className="field-label">
                Contorno en x = {xHigh}
              </span>
              <input
                value={bcRight}
                onChange={(e) => setBcRight(e.target.value)}
                spellCheck={false}
              />
            </label>
          </div>

          <LatexEditor
            label="Condición inicial u(x, 0) = f(x)"
            value={initial}
            onChange={setInitial}
            rows={2}
          />

          <DetailSlider value={detail} onChange={setDetail} />

          <button
            className="solve-button"
            onClick={handleSolve}
            disabled={loading}
          >
            {loading ? "Resolviendo…" : "Resolver con explicación detallada"}
          </button>
        </section>

        <section className="panel">
          <h2>Vista previa</h2>
          {result?.solution_latex ? (
            <>
              <div className="field-label">Solución final</div>
              <div className="latex-block">
                {/* react-katex usage avoided; the StepCard already
                    renders this nicely inside the Paso 6 card. */}
                <code style={{ fontSize: 13 }}>{result.solution_latex}</code>
              </div>
              <HeatPlot
                plot={result.plot_data}
                convergence={result.convergence_data}
              />
            </>
          ) : (
            <p style={{ color: "var(--text-muted)" }}>
              Configura el problema a la izquierda y pulsa{" "}
              <em>Resolver</em>. Verás la solución en serie, la superficie{" "}
              <em>u(x, t)</em> y la convergencia con N = 1, 5, 20, 100
              términos.
            </p>
          )}
        </section>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <strong>Error al resolver:</strong> {error}
        </div>
      )}

      {result && (
        <section className="results-section">
          <h2 style={{ fontFamily: "var(--font-ui)" }}>
            Desarrollo paso a paso
          </h2>
          {visibleSteps.map((step, i) => (
            <StepCard key={i} step={step} />
          ))}
        </section>
      )}
    </div>
  );
}
