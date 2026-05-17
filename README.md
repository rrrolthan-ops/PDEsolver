# PDESolver Pedagógico

Aplicación web educativa que resuelve EDPs clásicas de la física matemática
mostrando **cada paso del razonamiento** como lo haría un profesor en la
pizarra, no como una calculadora que devuelve la respuesta final.

## Estado actual

Este repositorio está en **Fase 1 (hito piloto)**. Lo que funciona hoy:

- **Ecuación del calor 1D** en una barra `[0, L]` con extremos a temperatura
  cero (Dirichlet homogéneas) y perfil inicial `f(x)` arbitrario, resuelta
  por **separación de variables**.
- Entrada manual por LaTeX.
- Salida estructurada en pasos (Paso 0–9) con plantillas pedagógicas
  deterministas en español, observaciones didácticas curadas, verificación
  simbólica de la solución y convergencia numérica de la serie.
- Frontend mínimo con editor LaTeX, tarjetas colapsables por paso,
  slider de nivel de detalle (Básico / Intermedio / Exhaustivo) y gráfico
  Plotly de `u(x, t)`.

Lo que **NO** está en este hito (pero sí en el plan): otras EDPs, otros
métodos, lenguaje natural, pipeline de visión, exportación a PDF,
biblioteca de problemas.

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

## Cómo probar el caso piloto

Una vez levantado el backend, prueba la ecuación del calor 1D vía curl:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "equation_latex": "u_t = alpha^2 * u_{xx}",
    "domain": {"x": [0, "L"], "t": [0, "infty"]},
    "boundary_conditions": [
      {"type": "dirichlet", "where": "x=0", "value": "0"},
      {"type": "dirichlet", "where": "x=L", "value": "0"}
    ],
    "initial_conditions": [
      {"order": 0, "value": "sin(pi*x/L)"}
    ],
    "parameters": {"alpha": "positive", "L": "positive"}
  }'
```

La respuesta es un `SolutionSteps` con ~25 pasos, incluyendo los tres
casos λ<0, λ=0, λ>0 desarrollados explícitamente.

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

- **Fase 2**: ecuación de onda, Laplace, Poisson; métodos D'Alembert,
  Green, Sturm-Liouville en geometrías estándar.
- **Fase 3**: entrada por lenguaje natural (clasificador LLM, nunca
  resolvedor).
- **Fase 4**: pipeline de visión (OpenCV + pix2tex + Nougat + Mathpix
  opcional).
- **Fase 5**: exportación a PDF, biblioteca de problemas, pulido.

## Licencia

Por definir.
