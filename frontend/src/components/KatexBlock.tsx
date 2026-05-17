import { useEffect, useRef } from "react";
import katex from "katex";

interface Props {
  latex: string;
  displayMode?: boolean;
}

/**
 * Render a LaTeX string with KaTeX.
 *
 * We use the imperative `katex.render` API (rather than react-katex)
 * because it gives us cleaner error handling and avoids a couple of
 * peer-dependency quirks. Errors are rendered in red so the student
 * sees that something went wrong rather than getting a blank box.
 */
export function KatexBlock({ latex, displayMode = true }: Props) {
  const ref = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    try {
      katex.render(latex, ref.current, {
        displayMode,
        throwOnError: false,
        strict: "ignore",
        macros: {
          "\\R": "\\mathbb{R}",
          "\\N": "\\mathbb{N}",
        },
      });
    } catch (e) {
      ref.current.innerHTML = `<span style="color:#c44e3a">[error LaTeX] ${String(e)}</span>`;
    }
  }, [latex, displayMode]);

  return <span ref={ref} className={displayMode ? "latex-block" : "latex-inline"} />;
}
