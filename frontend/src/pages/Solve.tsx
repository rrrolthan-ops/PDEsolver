import { useMemo, useState } from "react";
import { saveLibraryEntry, solveProblem } from "../api/client";
import type {
  BoundaryCondition,
  DetailLevel,
  InitialCondition,
  LibrarySource,
  PDEProblem,
  SolutionResponse,
  VisionExtractionResult,
} from "../api/types";
import { DetailSlider, shouldShow } from "../components/DetailSlider";
import { HeatPlot } from "../components/HeatPlot";
import { ImageUpload } from "../components/ImageUpload";
import { KatexBlock } from "../components/KatexBlock";
import { LatexEditor } from "../components/LatexEditor";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { NaturalLanguageInput } from "../components/NaturalLanguageInput";
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

type InputMode = "write" | "natural" | "image";

interface PendingNL {
  problem: PDEProblem;
  source: string;
  notes: string | null;
}

interface Props {
  mode: InputMode;
}

export function Solve({ mode }: Props) {
  // Manual editor state.
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

  // Natural-language: a parsed problem waiting for user confirmation.
  const [pendingNL, setPendingNL] = useState<PendingNL | null>(null);

  // Image extraction: parsed problem + transcription + preview.
  const [pendingImage, setPendingImage] = useState<VisionExtractionResult | null>(
    null,
  );

  // Provenance for the currently displayed result — used by the Save flow.
  const [lastSolved, setLastSolved] = useState<{
    problem: PDEProblem;
    source: LibrarySource;
    image_data_url: string | null;
  } | null>(null);

  const [saveStatus, setSaveStatus] = useState<
    "idle" | "saving" | "saved" | "error"
  >("idle");
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const buildManualProblem = (): PDEProblem => {
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

  const handleSolve = async (
    problem: PDEProblem,
    provenance: { source: LibrarySource; image_data_url: string | null },
  ) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSaveStatus("idle");
    setSaveMessage(null);
    setLastSolved(null);
    try {
      const resp = await solveProblem(problem);
      setResult(resp);
      setLastSolved({ problem, ...provenance });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleSolveManual = () =>
    handleSolve(buildManualProblem(), {
      source: "manual",
      image_data_url: null,
    });
  const handleSolvePending = () => {
    if (pendingNL)
      handleSolve(pendingNL.problem, {
        source: "natural",
        image_data_url: null,
      });
  };
  const handleSolvePendingImage = () => {
    if (pendingImage)
      handleSolve(pendingImage.problem, {
        source: "vision",
        image_data_url: pendingImage.image_preview_data_url,
      });
  };

  const handleSaveToLibrary = async () => {
    if (!result || !lastSolved) return;
    setSaveStatus("saving");
    setSaveMessage(null);
    try {
      const saved = await saveLibraryEntry({
        problem: lastSolved.problem,
        solution: result,
        source: lastSolved.source,
        image_data_url: lastSolved.image_data_url,
      });
      setSaveStatus("saved");
      setSaveMessage(`Guardado como "${saved.name}".`);
    } catch (e) {
      setSaveStatus("error");
      setSaveMessage(e instanceof Error ? e.message : String(e));
    }
  };

  const handleExportPdf = () => {
    // Browser-driven: the print stylesheet hides the dev chrome and lays
    // out the step cards as A4-friendly blocks. The user picks
    // "Save as PDF" in the system print dialog. No backend involvement.
    window.print();
  };

  const pushIntoManualEditor = (problem: PDEProblem) => {
    setEquation(problem.equation_latex);
    const dx = problem.domain.x;
    if (dx) {
      setXLow(dx[0]);
      setXHigh(dx[1]);
    }
    const bc0 = problem.boundary_conditions[0];
    const bc1 = problem.boundary_conditions[1];
    if (bc0) setBcLeft(bc0.value);
    if (bc1) setBcRight(bc1.value);
    const ic0 = problem.initial_conditions[0];
    if (ic0) setInitial(ic0.value);
  };

  const handleEditPending = () => {
    if (!pendingNL) return;
    pushIntoManualEditor(pendingNL.problem);
    setPendingNL(null);
  };
  const handleEditPendingImage = () => {
    if (!pendingImage) return;
    pushIntoManualEditor(pendingImage.problem);
    setPendingImage(null);
  };

  const visibleSteps =
    result?.steps.filter((s) => shouldShow(s.level, detail)) ?? [];

  // What to render in the left column depends on the active tab.
  const leftPanel = useMemo(() => {
    if (mode === "image") {
      if (pendingImage) {
        return (
          <ImageConfirmationPanel
            extraction={pendingImage}
            onSolve={handleSolvePendingImage}
            onEdit={handleEditPendingImage}
            onDiscard={() => setPendingImage(null)}
            loading={loading}
          />
        );
      }
      return <ImageUpload onExtracted={setPendingImage} />;
    }
    if (mode === "natural") {
      if (pendingNL) {
        return (
          <ConfirmationPanel
            pending={pendingNL}
            onSolve={handleSolvePending}
            onEdit={handleEditPending}
            onDiscard={() => setPendingNL(null)}
            loading={loading}
          />
        );
      }
      return (
        <NaturalLanguageInput
          onParsed={(problem, source, notes) =>
            setPendingNL({ problem, source, notes })
          }
        />
      );
    }
    // Manual editor.
    return (
      <ManualEditorPanel
        equation={equation}
        setEquation={setEquation}
        xLow={xLow}
        setXLow={setXLow}
        xHigh={xHigh}
        setXHigh={setXHigh}
        bcLeft={bcLeft}
        setBcLeft={setBcLeft}
        bcRight={bcRight}
        setBcRight={setBcRight}
        initial={initial}
        setInitial={setInitial}
        detail={detail}
        setDetail={setDetail}
        loading={loading}
        onSolve={handleSolveManual}
      />
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, pendingNL, pendingImage, equation, xLow, xHigh, bcLeft, bcRight, initial, detail, loading]);

  return (
    <div>
      <div className="solve-grid">
        {leftPanel}

        <section className="panel">
          <h2>Vista previa</h2>
          {loading ? (
            <div className="preview-skeleton" role="status" aria-live="polite">
              <LoadingSpinner
                showHint
                label="Resolviendo el problema…"
              />
              <div className="preview-skeleton-block short" />
              <div className="preview-skeleton-block" />
              <div className="preview-skeleton-block tall" />
            </div>
          ) : result?.solution_latex ? (
            <>
              <div className="field-label">Solución final</div>
              <div className="latex-block">
                <code style={{ fontSize: 13 }}>{result.solution_latex}</code>
              </div>
              <HeatPlot
                plot={result.plot_data}
                convergence={result.convergence_data}
              />
            </>
          ) : (
            <p style={{ color: "var(--text-muted)" }}>
              {mode === "image"
                ? "Sube una foto del problema. Verás la imagen y la transcripción lado a lado para confirmar antes de resolver."
                : mode === "natural"
                  ? "Describe el problema a la izquierda y pulsa Interpretar. Después podrás confirmar la interpretación antes de resolver."
                  : "Configura el problema a la izquierda y pulsa Resolver. Verás la solución, la superficie u(x, t) y la convergencia."}
            </p>
          )}
        </section>
      </div>

      {error && (
        <div className="error-banner" role="alert" data-testid="error-banner">
          <div>
            <strong>Error al resolver:</strong> {error}
          </div>
          <button
            type="button"
            className="solve-button"
            onClick={() => setError(null)}
            style={{
              background: "transparent",
              color: "var(--accent)",
              border: "1px solid var(--accent)",
              padding: "4px 12px",
              fontSize: 13,
              marginLeft: 12,
            }}
          >
            Cerrar
          </button>
        </div>
      )}

      {result && (
        <section className="results-section">
          <div
            data-no-print="true"
            style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}
          >
            <button
              type="button"
              className="solve-button"
              onClick={handleSaveToLibrary}
              disabled={saveStatus === "saving" || !lastSolved}
              style={{
                background: "transparent",
                color: "var(--accent)",
                border: "1px solid var(--accent)",
              }}
            >
              {saveStatus === "saving"
                ? "Guardando…"
                : saveStatus === "saved"
                  ? "Guardado ✓"
                  : "Guardar en biblioteca"}
            </button>
            <button
              type="button"
              className="solve-button"
              onClick={handleExportPdf}
            >
              Exportar a PDF
            </button>
            {saveMessage && (
              <span
                style={{
                  fontSize: 13,
                  color:
                    saveStatus === "error"
                      ? "var(--pitfall)"
                      : "var(--text-muted)",
                }}
              >
                {saveMessage}
              </span>
            )}
          </div>
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

// ---------------------------------------------------------------------------
// Manual editor (extracted for clarity)
// ---------------------------------------------------------------------------

interface ManualEditorProps {
  equation: string;
  setEquation: (v: string) => void;
  xLow: string;
  setXLow: (v: string) => void;
  xHigh: string;
  setXHigh: (v: string) => void;
  bcLeft: string;
  setBcLeft: (v: string) => void;
  bcRight: string;
  setBcRight: (v: string) => void;
  initial: string;
  setInitial: (v: string) => void;
  detail: DetailLevel;
  setDetail: (v: DetailLevel) => void;
  loading: boolean;
  onSolve: () => void;
}

function ManualEditorPanel(props: ManualEditorProps) {
  return (
    <section className="panel">
      <h2>Planteamiento del problema</h2>
      <LatexEditor
        label="EDP (usa notación física: u_t, u_xx, …)"
        value={props.equation}
        onChange={props.setEquation}
        rows={2}
      />
      <div className="bc-row">
        <label className="field">
          <span className="field-label">Dominio: x mínimo</span>
          <input
            value={props.xLow}
            onChange={(e) => props.setXLow(e.target.value)}
            spellCheck={false}
          />
        </label>
        <label className="field">
          <span className="field-label">Dominio: x máximo</span>
          <input
            value={props.xHigh}
            onChange={(e) => props.setXHigh(e.target.value)}
            spellCheck={false}
          />
        </label>
      </div>
      <div className="bc-row">
        <label className="field">
          <span className="field-label">Contorno en x = {props.xLow}</span>
          <input
            value={props.bcLeft}
            onChange={(e) => props.setBcLeft(e.target.value)}
            spellCheck={false}
          />
        </label>
        <label className="field">
          <span className="field-label">Contorno en x = {props.xHigh}</span>
          <input
            value={props.bcRight}
            onChange={(e) => props.setBcRight(e.target.value)}
            spellCheck={false}
          />
        </label>
      </div>
      <LatexEditor
        label="Condición inicial u(x, 0) = f(x)"
        value={props.initial}
        onChange={props.setInitial}
        rows={2}
      />
      <DetailSlider value={props.detail} onChange={props.setDetail} />
      <button
        className="solve-button"
        onClick={props.onSolve}
        disabled={props.loading}
      >
        {props.loading ? "Resolviendo…" : "Resolver con explicación detallada"}
      </button>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Confirmation panel (shown after natural-language parse)
// ---------------------------------------------------------------------------

interface ConfirmationProps {
  pending: PendingNL;
  loading: boolean;
  onSolve: () => void;
  onEdit: () => void;
  onDiscard: () => void;
}

function ConfirmationPanel({
  pending,
  loading,
  onSolve,
  onEdit,
  onDiscard,
}: ConfirmationProps) {
  const p = pending.problem;
  return (
    <section className="panel">
      <h2>Confirma la interpretación</h2>
      <p style={{ marginTop: 0, color: "var(--text-muted)", fontSize: 14 }}>
        Esto es lo que entendí. Revísalo y pulsa <strong>Resolver</strong>{" "}
        si es correcto, o <strong>Editar manualmente</strong> para ajustarlo.
      </p>

      <SummaryRow label="Tipo" value={p.equation_kind} />
      <SummaryRow label="EDP" value={p.equation_latex} mono />
      {p.geometry && <SummaryRow label="Geometría" value={p.geometry} />}
      <SummaryRow
        label="Dominio"
        value={describeDomain(p)}
      />
      <SummaryRow
        label="Condiciones de contorno"
        value={
          p.boundary_conditions.length === 0
            ? "(ninguna)"
            : p.boundary_conditions
                .map((bc) => `${bc.type}: ${bc.where} → ${bc.value}`)
                .join("; ")
        }
      />
      <SummaryRow
        label="Condiciones iniciales"
        value={
          p.initial_conditions.length === 0
            ? "(ninguna)"
            : p.initial_conditions
                .map((ic) =>
                  ic.order === 0
                    ? `u(·, 0) = ${ic.value}`
                    : `u_t(·, 0) = ${ic.value}`,
                )
                .join("; ")
        }
      />
      {p.source_term && <SummaryRow label="Término fuente" value={p.source_term} mono />}

      <SummaryRow
        label="Interpretado por"
        value={pending.source === "deterministic" ? "Plantilla determinista" : pending.source}
      />
      {pending.notes && (
        <div
          className="observation observation-pitfall"
          style={{ marginTop: 12 }}
        >
          <span className="obs-label">Nota:</span> {pending.notes}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button className="solve-button" onClick={onSolve} disabled={loading}>
          {loading ? "Resolviendo…" : "Resolver"}
        </button>
        <button
          className="solve-button"
          onClick={onEdit}
          style={{ background: "transparent", color: "var(--accent)", border: "1px solid var(--accent)" }}
        >
          Editar manualmente
        </button>
        <button
          className="solve-button"
          onClick={onDiscard}
          style={{ background: "transparent", color: "var(--text-muted)", border: "1px solid var(--border)" }}
        >
          Descartar
        </button>
      </div>
    </section>
  );
}

function SummaryRow({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div className="field-label">{label}</div>
      <div
        style={{
          fontFamily: mono ? "var(--font-mono)" : "inherit",
          fontSize: 14,
          padding: "6px 8px",
          background: "var(--surface-2)",
          borderRadius: 4,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function describeDomain(p: PDEProblem): string {
  const parts: string[] = [];
  const axes = ["x", "y", "z", "t"] as const;
  for (const ax of axes) {
    const v = p.domain[ax];
    if (v) parts.push(`${ax} ∈ [${v[0]}, ${v[1]}]`);
  }
  return parts.join(", ") || "(sin dominio)";
}

// ---------------------------------------------------------------------------
// Image confirmation panel (after /vision/extract)
// ---------------------------------------------------------------------------

interface ImageConfirmationProps {
  extraction: VisionExtractionResult;
  loading: boolean;
  onSolve: () => void;
  onEdit: () => void;
  onDiscard: () => void;
}

const CONFIDENCE_LABEL: Record<string, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

const CONFIDENCE_COLOR: Record<string, string> = {
  high: "var(--intuition)",
  medium: "var(--text-muted)",
  low: "var(--pitfall)",
};

function ImageConfirmationPanel({
  extraction,
  loading,
  onSolve,
  onEdit,
  onDiscard,
}: ImageConfirmationProps) {
  const { problem: p } = extraction;
  return (
    <section className="panel">
      <h2>Confirma la transcripción</h2>
      <p style={{ marginTop: 0, color: "var(--text-muted)", fontSize: 14 }}>
        Compara la foto con el LaTeX transcrito. Si está bien, pulsa{" "}
        <strong>Resolver</strong>. Si hay errores, usa{" "}
        <strong>Editar manualmente</strong> para corregir.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
        <div>
          <div className="field-label">Imagen original</div>
          {extraction.image_preview_data_url && (
            <img
              src={extraction.image_preview_data_url}
              alt="Imagen procesada"
              style={{
                maxWidth: "100%",
                maxHeight: 240,
                borderRadius: 6,
                border: "1px solid var(--border)",
              }}
            />
          )}
        </div>
        <div>
          <div className="field-label">Transcripción LaTeX</div>
          <div
            style={{
              padding: "10px 12px",
              background: "var(--surface-2)",
              borderRadius: 6,
              minHeight: 80,
              overflowX: "auto",
            }}
          >
            <KatexBlock latex={extraction.transcribed_latex || "(vacío)"} />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: 12, fontSize: 14 }}>
        <strong>Confianza del modelo:</strong>{" "}
        <span style={{ color: CONFIDENCE_COLOR[extraction.confidence] }}>
          {CONFIDENCE_LABEL[extraction.confidence]}
        </span>
        {extraction.confidence === "low" && (
          <span style={{ color: "var(--pitfall)", marginLeft: 8 }}>
            ⚠ Revisa cuidadosamente antes de resolver.
          </span>
        )}
      </div>

      <SummaryRow label="Tipo" value={p.equation_kind} />
      <SummaryRow label="EDP" value={p.equation_latex} mono />
      {p.geometry && <SummaryRow label="Geometría" value={p.geometry} />}
      <SummaryRow label="Dominio" value={describeDomain(p)} />
      <SummaryRow
        label="Condiciones de contorno"
        value={
          p.boundary_conditions.length === 0
            ? "(ninguna)"
            : p.boundary_conditions
                .map((bc) => `${bc.type}: ${bc.where} → ${bc.value}`)
                .join("; ")
        }
      />
      <SummaryRow
        label="Condiciones iniciales"
        value={
          p.initial_conditions.length === 0
            ? "(ninguna)"
            : p.initial_conditions
                .map((ic) =>
                  ic.order === 0
                    ? `u(·, 0) = ${ic.value}`
                    : `u_t(·, 0) = ${ic.value}`,
                )
                .join("; ")
        }
      />
      <SummaryRow label="Procesado por" value={extraction.engine} />
      {extraction.notes && (
        <div
          className="observation observation-pitfall"
          style={{ marginTop: 12 }}
        >
          <span className="obs-label">Nota:</span> {extraction.notes}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button className="solve-button" onClick={onSolve} disabled={loading}>
          {loading ? "Resolviendo…" : "Resolver"}
        </button>
        <button
          className="solve-button"
          onClick={onEdit}
          style={{
            background: "transparent",
            color: "var(--accent)",
            border: "1px solid var(--accent)",
          }}
        >
          Editar manualmente
        </button>
        <button
          className="solve-button"
          onClick={onDiscard}
          style={{
            background: "transparent",
            color: "var(--text-muted)",
            border: "1px solid var(--border)",
          }}
        >
          Descartar
        </button>
      </div>
    </section>
  );
}
