# PDESolver Pedagógico

Aplicación web educativa que resuelve EDPs clásicas de la física matemática
mostrando **cada paso del razonamiento** como lo haría un profesor en la
pizarra, no como una calculadora que devuelve la respuesta final.

## Estado actual

Este repositorio está en **Fase 2-A**. Lo que funciona hoy:

| EDP | Dominio | Método | Slug |
|---|---|---|---|
| Calor `u_t = α² u_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `separation_of_variables` |
| Onda `u_tt = c² u_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `sov_wave_1d` |
| Onda `u_tt = c² u_xx` | `x ∈ ℝ` | Fórmula de D'Alembert | `dalembert_wave_1d` |
| Laplace `∇²u = 0` | `[0, a] × [0, b]`, Dirichlet | Separación de variables | `sov_laplace_rect` |

Para cada método la salida es la misma estructura de **10 pasos** (Paso 0–9):
planteamiento, clasificación, elección de método, desarrollo (incluyendo
los tres casos de λ cuando aplica), aplicación de BCs/ICs, solución
final, verificación simbólica, visualización y lectura física.

Lo que **NO** está todavía: Poisson con función de Green, Laplace en
disco (Bessel), Helmholtz, telégrafo, Schrödinger, biarmónica,
coordenadas cilíndricas/esféricas (Bessel/Legendre/armónicos esféricos),
método de imágenes, método de las características en su versión general.
Llegan en Fase 2-B/C. Tampoco: lenguaje natural (Fase 3), visión
(Fase 4), exportación PDF y biblioteca (Fase 5).

## Arquitectura

```
pdesolver-pedagogico/
├── backend/                FastAPI + SymPy (motor simbólico)
│   ├── app/
│   │   ├── solver/         núcleo pedagógico
│   │   │   ├── core/       Step, PDEProblem, clasificación
│   │   │   ├── methods/    separation_of_variables.py (otros: stubs)
│   │   │   ├── equations/  plantillas por EDP (heat.py implementada)
│   │   │   ├── pedagogy/   templates y observaciones didácticas
│   │   │   ├── verify.py   sustituye solución en EDP y comprueba
│   │   │   └── numerics.py convergencia N = 1, 5, 20, 100
│   │   ├── parser/         LaTeX → SymPy (notación física u_t, u_xx…)
│   │   └── api/            endpoints REST
│   └── tests/              pytest con 5+ problemas de Haberman/Tijonov
├── frontend/               React + TS + Vite + KaTeX + Plotly
└── docker/                 Dockerfiles (visión queda comentada hasta Fase 4)
```

### Decisiones clave

- **SymPy** como motor simbólico, NumPy/SciPy para verificación numérica.
- **KaTeX** sobre MathJax: decenas de fórmulas por página justifican
  la diferencia de rendimiento.
- **Las explicaciones NO se generan con LLM** en runtime. Son plantillas
  deterministas atadas a la estructura simbólica del problema, para
  garantizar corrección matemática. Los LLMs se reservan (en fases
  posteriores) solo para clasificar fragmentos LaTeX extraídos de imágenes.
- `SolutionSteps` es una lista plana de `Step(title, explanation_md,
  latex, sympy_expr, observations, level)`. El campo `level` permite que
  el frontend filtre por nivel de detalle sin re-resolver.

## Instalación local (sin Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173.

### Con Docker

```bash
docker compose up --build
```

## Cómo probar los métodos

### Calor 1D

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_t = alpha^2 * u_{xx}",
  "equation_kind": "heat",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "sin(pi*x/L)"}],
  "parameters": {"alpha": "positive", "L": "positive"}
}'
```

### Onda 1D acotada (separación de variables)

Cuerda fija en sus extremos. Necesita **dos** condiciones iniciales
(posición y velocidad):

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{tt} = c^2 * u_{xx}",
  "equation_kind": "wave",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [
    {"order": 0, "value": "sin(pi*x/L)"},
    {"order": 1, "value": "0"}
  ],
  "parameters": {"c": "positive", "L": "positive"}
}'
```

### Onda 1D infinita (D'Alembert)

Dominio `x ∈ ℝ`, sin condiciones de contorno:

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{tt} = c^2 * u_{xx}",
  "equation_kind": "wave",
  "domain": {"x": ["-infty", "infty"], "t": ["0", "infty"]},
  "boundary_conditions": [],
  "initial_conditions": [
    {"order": 0, "value": "exp(-x^2)"},
    {"order": 1, "value": "0"}
  ],
  "parameters": {"c": "positive"}
}'
```

### Laplace en rectángulo

Tres lados a cero, un lado con dato:

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{xx} + u_{yy} = 0",
  "equation_kind": "laplace",
  "domain": {"x": ["0", "a"], "y": ["0", "b"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=a", "value": "0"},
    {"type": "dirichlet", "where": "y=0", "value": "0"},
    {"type": "dirichlet", "where": "y=b", "value": "sin(pi*x/a)"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"a": "positive", "b": "positive"}
}'
```

## Extensión: añadir un método nuevo

Cada método vive en `backend/app/solver/methods/` y implementa la interfaz
`Method.solve(problem: PDEProblem) -> SolutionSteps` definida en
`methods/base.py`. Para añadir, p. ej., D'Alembert:

1. Crear `methods/dalembert.py` con una clase `DAlembertMethod(Method)`.
2. Registrarla en `solver/core/method_picker.py` con su heurística de
   elegibilidad (ej. "EDP de onda 1D, dominio infinito").
3. Añadir plantillas pedagógicas en `solver/pedagogy/templates.py` para
   los pasos específicos del método.
4. Añadir tests con problemas de referencia.

## Tests

```bash
cd backend
pytest -v
```

Los tests del solver comparan tanto la **forma estructural** de
`SolutionSteps` (presencia de pasos clave) como la **igualdad simbólica**
con soluciones de referencia tomadas de Haberman ("Applied PDEs") y
Tijonov–Samarsky ("Equations of Mathematical Physics").

## Próximos hitos

- **Fase 2-B**: Poisson con función de Green en geometrías estándar,
  Laplace en disco (Bessel-Fourier), Helmholtz acotado, telégrafo.
- **Fase 2-C**: Schrödinger libre y con pozo, coordenadas
  cilíndricas/esféricas (Bessel, Legendre, armónicos esféricos),
  método de imágenes, biarmónica.
- **Fase 3**: entrada por lenguaje natural (clasificador LLM, nunca
  resolvedor).
- **Fase 4**: pipeline de visión (OpenCV + pix2tex + Nougat + Mathpix
  opcional).
- **Fase 5**: exportación a PDF, biblioteca de problemas, pulido.

## Licencia

Por definir.
