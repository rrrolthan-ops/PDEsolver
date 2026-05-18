import { useEffect, useState } from "react";
import {
  deleteLibraryEntry,
  getLibraryEntry,
  listLibrary,
} from "../api/client";
import type {
  LibraryItem,
  LibraryListItem,
  PDEProblem,
  SolutionResponse,
} from "../api/types";
import { DetailSlider, shouldShow } from "../components/DetailSlider";
import { HeatPlot } from "../components/HeatPlot";
import { StepCard } from "../components/StepCard";

const KIND_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "heat", label: "Calor" },
  { value: "wave", label: "Onda" },
  { value: "laplace", label: "Laplace" },
  { value: "poisson", label: "Poisson" },
  { value: "helmholtz", label: "Helmholtz" },
  { value: "schrodinger", label: "Schrödinger" },
  { value: "telegraph", label: "Telégrafo" },
  { value: "biharmonic", label: "Biarmónica" },
  { value: "general", label: "Otro" },
];

interface Props {
  /**
   * Called when the user clicks a library entry. The parent can navigate
   * away from the library and show the solution; here we just keep it
   * simple and toggle a detail view inside the library page itself.
   */
  onOpen?: (item: LibraryItem) => void;
}

export function Library({ onOpen }: Props) {
  const [items, setItems] = useState<LibraryListItem[]>([]);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<LibraryItem | null>(null);

  const reload = async () => {
    setLoading(true);
    setError(null);
    try {
      const rows = await listLibrary(filter ? { equation_kind: filter } : undefined);
      setItems(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const handleOpen = async (id: string) => {
    try {
      const full = await getLibraryEntry(id);
      setOpen(full);
      onOpen?.(full);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`¿Eliminar "${name}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    try {
      await deleteLibraryEntry(id);
      setItems(items.filter((i) => i.id !== id));
      if (open?.id === id) setOpen(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  if (open) {
    return (
      <LibraryDetail
        item={open}
        onClose={() => setOpen(null)}
        onDelete={() => handleDelete(open.id, open.name)}
      />
    );
  }

  return (
    <section>
      <div className="library-filter-bar">
        <label htmlFor="kind-filter">Filtrar por EDP:</label>
        <select
          id="kind-filter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          {KIND_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <span style={{ color: "var(--text-muted)", marginLeft: 8 }}>
          {loading ? "Cargando…" : `${items.length} problema${items.length === 1 ? "" : "s"}`}
        </span>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      {!loading && items.length === 0 && (
        <p style={{ color: "var(--text-muted)" }}>
          Tu biblioteca está vacía. Resuelve un problema y pulsa{" "}
          <strong>Guardar en biblioteca</strong> para almacenarlo aquí.
        </p>
      )}

      <div className="library-grid">
        {items.map((item) => (
          <article
            key={item.id}
            className="library-card"
            onClick={() => handleOpen(item.id)}
          >
            {item.image_data_url ? (
              <img className="thumb" src={item.image_data_url} alt="" />
            ) : (
              <div className="thumb-placeholder">{item.method_slug}</div>
            )}
            <h3>{item.name}</h3>
            <div style={{ marginBottom: 6 }}>
              <span className="library-tags">{item.equation_kind}</span>
              <span className="library-tags">{item.source}</span>
            </div>
            <div className="meta">
              {new Date(item.created_at + "Z").toLocaleString()}
            </div>
            <button
              type="button"
              style={{
                marginTop: 8,
                background: "transparent",
                border: "none",
                color: "var(--pitfall)",
                cursor: "pointer",
                padding: 0,
                fontSize: 12,
                fontFamily: "var(--font-ui)",
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(item.id, item.name);
              }}
            >
              Eliminar
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------

interface DetailProps {
  item: LibraryItem;
  onClose: () => void;
  onDelete: () => void;
}

function LibraryDetail({ item, onClose, onDelete }: DetailProps) {
  const [detail, setDetail] = useState<"basic" | "intermediate" | "exhaustive">(
    "exhaustive",
  );
  const visibleSteps = item.solution.steps.filter((s) =>
    shouldShow(s.level, detail),
  );

  return (
    <section>
      <div
        data-no-print="true"
        style={{ display: "flex", gap: 8, marginBottom: 12 }}
      >
        <button
          type="button"
          className="solve-button"
          style={{
            background: "transparent",
            color: "var(--accent)",
            border: "1px solid var(--accent)",
          }}
          onClick={onClose}
        >
          ← Volver a la biblioteca
        </button>
        <button
          type="button"
          className="solve-button"
          onClick={() => window.print()}
        >
          Exportar a PDF
        </button>
        <button
          type="button"
          className="solve-button"
          style={{
            background: "transparent",
            color: "var(--pitfall)",
            border: "1px solid var(--pitfall)",
          }}
          onClick={onDelete}
        >
          Eliminar
        </button>
      </div>

      <h2 style={{ fontFamily: "var(--font-ui)" }}>{item.name}</h2>
      <p style={{ color: "var(--text-muted)" }}>
        Método: <code>{item.method_slug}</code> · Origen: {item.source} ·
        Guardado el {new Date(item.created_at + "Z").toLocaleString()}
      </p>

      {item.image_data_url && (
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ fontFamily: "var(--font-ui)" }}>Imagen original</h3>
          <img
            src={item.image_data_url}
            alt="Imagen original del problema"
            style={{
              maxWidth: 400,
              borderRadius: 6,
              border: "1px solid var(--border)",
            }}
          />
        </div>
      )}

      <DetailSlider value={detail} onChange={setDetail} />

      <SolutionView problem={item.problem} solution={item.solution} />

      <h2 style={{ fontFamily: "var(--font-ui)" }}>Desarrollo paso a paso</h2>
      {visibleSteps.map((step, i) => (
        <StepCard key={i} step={step} />
      ))}
    </section>
  );
}

function SolutionView({
  problem,
  solution,
}: {
  problem: PDEProblem;
  solution: SolutionResponse;
}) {
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <h3 style={{ fontFamily: "var(--font-ui)", marginTop: 0 }}>
        Solución
      </h3>
      <div className="field-label">EDP</div>
      <div className="latex-block">
        <code>{problem.equation_latex}</code>
      </div>
      <div className="field-label">Solución final (LaTeX)</div>
      <div className="latex-block">
        <code style={{ fontSize: 13 }}>{solution.solution_latex}</code>
      </div>
      <HeatPlot
        plot={solution.plot_data}
        convergence={solution.convergence_data}
      />
    </div>
  );
}
