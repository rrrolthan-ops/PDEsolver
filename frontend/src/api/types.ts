// Mirrors `backend/app/schemas/solution.py` and `problem.py`.
// Keep these in sync when you change the Pydantic schemas.

export type DetailLevel = "basic" | "intermediate" | "exhaustive";

export type StepKind =
  | "statement"
  | "classification"
  | "method_choice"
  | "development"
  | "boundary"
  | "initial"
  | "final"
  | "verification"
  | "visualization"
  | "interpretation"
  | "observation";

export interface DidacticObservation {
  kind: "pitfall" | "intuition" | "theorem" | "alternative";
  text_md: string;
}

export interface Step {
  kind: StepKind;
  title: string;
  explanation_md: string;
  latex: string;
  sympy_repr: string | null;
  observations: DidacticObservation[];
  level: DetailLevel;
}

export interface PlotData {
  x: number[];
  t: number[];
  u: number[][];
}

export interface ConvergenceData {
  x: number[];
  t_eval: number;
  snapshots: Record<string, number[]>;
}

export interface SolutionResponse {
  method: string;
  steps: Step[];
  solution_latex: string;
  solution_sympy_repr: string | null;
  plot_data: PlotData | null;
  convergence_data: ConvergenceData | null;
  verified: boolean;
}

export interface BoundaryCondition {
  type: "dirichlet" | "neumann" | "robin" | "periodic";
  where: string;
  value: string;
  coefficients?: Record<string, string> | null;
}

export interface InitialCondition {
  order: number;
  value: string;
}

export interface Domain {
  x?: [string, string] | null;
  y?: [string, string] | null;
  z?: [string, string] | null;
  t?: [string, string] | null;
}

export type Geometry =
  | "interval"
  | "rectangle"
  | "disk"
  | "halfplane"
  | "line"
  | "halfline"
  | "box"
  | "cylinder"
  | "sphere";

export interface PDEProblem {
  equation_latex: string;
  equation_kind: string;
  source_term?: string | null;
  geometry?: Geometry | null;
  domain: Domain;
  boundary_conditions: BoundaryCondition[];
  initial_conditions: InitialCondition[];
  parameters: Record<string, string>;
  notes?: string | null;
}
