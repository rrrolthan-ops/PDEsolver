import Plot from "react-plotly.js";
import type {
  ConvergenceData,
  LinePlot as LinePlotPayload,
  PlotData,
  SurfaceXTPlot,
  SurfaceXYPlot,
} from "../api/types";

interface Props {
  plot: PlotData | null;
  convergence: ConvergenceData | null;
}

/**
 * Plot dispatcher.
 *
 * Three shapes flow from the backend, distinguished by the `kind` tag:
 *
 *   surface_xt  → 3D surface of u(x, t)   (heat/wave/Laplace 1D etc.)
 *   surface_xy  → 3D surface of u(x, y)   (disk, ball slice, …)
 *   line        → 1D plot of u(x)         (Poisson 1D, beam, …)
 *
 * Legacy responses without a `kind` field are treated as `surface_xt`
 * so the contract stays backward-compatible.
 *
 * The convergence panel only shows up alongside surface plots; the 1D
 * methods don't carry a partial-sum series with `N = 1, 5, 20, 100`
 * snapshots.
 */
export function HeatPlot({ plot, convergence }: Props) {
  if (!plot) return null;
  const kind = plot.kind ?? "surface_xt";

  return (
    <div>
      {kind === "surface_xt" && <SurfaceXT plot={plot as SurfaceXTPlot} />}
      {kind === "surface_xy" && <SurfaceXY plot={plot as SurfaceXYPlot} />}
      {kind === "line" && <Line plot={plot as LinePlotPayload} />}

      {convergence && kind !== "line" && (
        <Plot
          data={
            Object.entries(convergence.snapshots).map(([n, ys]) => ({
              type: "scatter",
              mode: "lines",
              name: `N = ${n}`,
              x: convergence.x,
              y: ys,
            })) as any
          }
          layout={{
            title: { text: `Convergencia de la serie en t = ${convergence.t_eval}` } as any,
            xaxis: { title: { text: "x" } as any },
            yaxis: { title: { text: "u" } as any },
            autosize: true,
            height: 320,
            margin: { l: 50, r: 20, t: 40, b: 40 },
            paper_bgcolor: "transparent",
            font: { family: "system-ui, sans-serif" },
          }}
          useResizeHandler
          style={{ width: "100%" }}
        />
      )}
    </div>
  );
}

// --- Variants ------------------------------------------------------------

function SurfaceXT({ plot }: { plot: SurfaceXTPlot }) {
  return (
    <Plot
      data={
        [
          {
            type: "surface",
            x: plot.x,
            y: plot.t,
            z: plot.u,
            colorscale: "Hot",
            showscale: false,
          },
        ] as any
      }
      layout={{
        title: { text: "u(x, t)" } as any,
        autosize: true,
        height: 380,
        margin: { l: 0, r: 0, t: 30, b: 0 },
        scene: {
          xaxis: { title: { text: "x" } as any },
          yaxis: { title: { text: "t" } as any },
          zaxis: { title: { text: "u" } as any },
        },
        paper_bgcolor: "transparent",
        font: { family: "system-ui, sans-serif" },
      }}
      useResizeHandler
      style={{ width: "100%" }}
    />
  );
}

function SurfaceXY({ plot }: { plot: SurfaceXYPlot }) {
  const xLabel = plot.x_label ?? "x";
  const yLabel = plot.y_label ?? "y";
  return (
    <Plot
      data={
        [
          {
            type: "surface",
            x: plot.x,
            y: plot.y,
            z: plot.u,
            colorscale: "Viridis",
            showscale: false,
            connectgaps: false,
          },
        ] as any
      }
      layout={{
        title: { text: `u(${xLabel}, ${yLabel})` } as any,
        autosize: true,
        height: 380,
        margin: { l: 0, r: 0, t: 30, b: 0 },
        scene: {
          xaxis: { title: { text: xLabel } as any },
          yaxis: { title: { text: yLabel } as any },
          zaxis: { title: { text: "u" } as any },
        },
        paper_bgcolor: "transparent",
        font: { family: "system-ui, sans-serif" },
      }}
      useResizeHandler
      style={{ width: "100%" }}
    />
  );
}

function Line({ plot }: { plot: LinePlotPayload }) {
  const xLabel = plot.x_label ?? "x";
  const yLabel = plot.y_label ?? "u(x)";
  return (
    <Plot
      data={
        [
          {
            type: "scatter",
            mode: "lines",
            x: plot.x,
            y: plot.u,
            line: { width: 2 },
          },
        ] as any
      }
      layout={{
        title: { text: yLabel } as any,
        xaxis: { title: { text: xLabel } as any, zeroline: true },
        yaxis: { title: { text: yLabel } as any, zeroline: true },
        autosize: true,
        height: 360,
        margin: { l: 50, r: 20, t: 40, b: 50 },
        paper_bgcolor: "transparent",
        font: { family: "system-ui, sans-serif" },
      }}
      useResizeHandler
      style={{ width: "100%" }}
    />
  );
}
