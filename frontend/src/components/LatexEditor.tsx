import { useEffect, useState } from "react";
import { KatexBlock } from "./KatexBlock";

interface Props {
  value: string;
  onChange: (v: string) => void;
  label?: string;
  preview?: boolean;
  rows?: number;
}

/**
 * A minimal LaTeX editor: a textarea on the left with a live KaTeX
 * preview underneath. Phase 1 keeps this plain; a richer editor with
 * symbol palette / autocomplete is a Phase 5 polish task.
 */
export function LatexEditor({
  value,
  onChange,
  label,
  preview = true,
  rows = 2,
}: Props) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), 200);
    return () => clearTimeout(id);
  }, [value]);

  return (
    <label className="field">
      {label && <span className="field-label">{label}</span>}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        spellCheck={false}
      />
      {preview && debounced && (
        <div className="latex-block" aria-label="Vista previa">
          <KatexBlock latex={debounced} />
        </div>
      )}
    </label>
  );
}
