import Plot from "react-plotly.js";
import type { ConvergenceData, PlotData } from "../api/types";

interface Props {
  plot: PlotData | null;
  convergence: ConvergenceData | null;
}

/**
 * Two plots side by side:
 *  - 3D surface u(x, t).
 *  - Convergence: partial sums N = 1, 5, 20, 100 at t = 0.
 *
 * The convergence panel is the one students actually learn from: it
 * shows the Fourier series approximating the initial profile as more
 * modes are added. The surface is "icing".
 */
export function HeatPlot({ plot, convergence }: Props) {
  return (
    <div>
      {plot && (
        <Plot
          data={[
            {
              type: "surface",
              x: plot.x,
              y: plot.t,
              z: plot.u,
              colorscale: "Hot",
              showscale: false,
            } as any,
          ]}
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
      )}

      {convergence && (
        <Plot
          data={Object.entries(convergence.snapshots).map(([n, ys]) => ({
            type: "scatter",
            mode: "lines",
            name: `N = ${n}`,
            x: convergence.x,
            y: ys,
          })) as any}
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
