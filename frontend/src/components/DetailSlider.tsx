import type { DetailLevel } from "../api/types";

interface Props {
  value: DetailLevel;
  onChange: (v: DetailLevel) => void;
}

const ORDER: DetailLevel[] = ["basic", "intermediate", "exhaustive"];
const LABEL: Record<DetailLevel, string> = {
  basic: "Básico",
  intermediate: "Intermedio",
  exhaustive: "Exhaustivo",
};

/**
 * Slider that picks how much detail the user wants to see.
 *
 * The backend always returns every step. The slider just decides which
 * `level` values to render. We never re-call the solver when the slider
 * moves — that would be wasteful and the math doesn't change.
 */
export function DetailSlider({ value, onChange }: Props) {
  const idx = ORDER.indexOf(value);
  return (
    <div className="detail-slider">
      <span>Detalle:</span>
      <input
        type="range"
        min={0}
        max={2}
        step={1}
        value={idx}
        onChange={(e) => onChange(ORDER[parseInt(e.target.value, 10)])}
      />
      <strong>{LABEL[value]}</strong>
    </div>
  );
}

export function shouldShow(stepLevel: DetailLevel, userLevel: DetailLevel): boolean {
  // basic ≤ intermediate ≤ exhaustive.
  return ORDER.indexOf(stepLevel) <= ORDER.indexOf(userLevel);
}
