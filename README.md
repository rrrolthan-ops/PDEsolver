# PDESolver Pedagógico

Aplicación web educativa que resuelve EDPs clásicas de la física matemática
mostrando **cada paso del razonamiento** como lo haría un profesor en la
pizarra, no como una calculadora que devuelve la respuesta final.

## Estado actual

Este repositorio está en **Fase 5**. Lo que funciona hoy:

**Entradas soportadas:**
- **Manual (LaTeX)** — disponible desde Fase 1.
- **Lenguaje natural** (Fase 3) — español o inglés. Capa determinista
  de plantillas + clasificador Claude opcional. El LLM **sólo
  clasifica**, nunca resuelve.
- **Imagen** (Fase 4) — sube una foto JPG/PNG/WEBP/HEIC de una página
  de libro, examen, pizarra o apunte. `claude-haiku-4-5` con visión
  lee la imagen, transcribe la fórmula como LaTeX, y la estructura
  como `PDEProblem` en una sola llamada. La transcripción se muestra
  **lado a lado con la foto original** para que el usuario confirme
  antes de resolver.

Las tres modalidades convergen en el mismo `PDEProblem` canónico
antes del solver, así que la calidad de la resolución es idéntica
independientemente del modo de entrada.

**Postprocesado** (NUEVO en Fase 5):
- **Biblioteca local** — guarda problemas resueltos en SQLite con
  miniatura (cuando proviene de imagen), filtro por tipo de EDP,
  apertura/eliminación y vista de detalle completa.
- **Exportación a PDF** — botón "Exportar a PDF" en la página de
  solución y en cada entrada de la biblioteca. Usa `window.print()` +
  CSS de impresión para producir un documento A4 limpio (sin la
  cabecera/pestañas/sliders del editor) listo para imprimir o guardar
  como PDF desde el navegador.

**Métodos de resolución:**

| EDP | Dominio | Método | Slug |
|---|---|---|---|
| Calor `u_t = α² u_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `separation_of_variables` |
| Calor `u_t = α² u_xx` | `x ∈ ℝ` | Transformada de Fourier / núcleo de Gauss | `fourier_heat_line` |
| Calor inhomogéneo `u_t = α² u_xx + f(x,t)` | `x ∈ ℝ` | Principio de Duhamel | `duhamel_heat` |
| Calor `u_t = α² u_xx`, `u(0,t)=h` | `x ∈ [0, ∞)` | Transformada de Laplace en `t` (solución erfc de Stokes) | `laplace_heat_halfline` |
| Calor `u_t = α²(u_rr + u_r/r)` | disco `r < R` axisimétrico | Bessel-Fourier | `sov_heat_disk` |
| Onda `u_tt = c² u_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `sov_wave_1d` |
| Onda `u_tt = c² u_xx` | `x ∈ ℝ` | Fórmula de D'Alembert | `dalembert_wave_1d` |
| Onda `u_tt = c²Δu` | disco `r < R` axisimétrico (tambor) | Bessel-Fourier | `sov_wave_disk` |
| Onda 2D `u_tt = c²(u_xx + u_yy)` | rectángulo `[0,a]×[0,b]`, Dirichlet 0 | SOV doble (modos `m,n`) | `sov_wave_rect` |
| Laplace `∇²u = 0` | `[0, a] × [0, b]` | Separación de variables | `sov_laplace_rect` |
| Laplace `∇²u = 0` | disco `r < R` | Separación en polares + Poisson | `sov_laplace_disk` |
| Laplace `∇²u = 0` | semiplano `y > 0` | Método de imágenes | `images_halfplane` |
| Laplace `∇²u = 0` | bola `r < R` axisimétrico | Legendre / multipolos | `sov_laplace_ball` |
| Poisson `−u'' = f(x)` | `[0, L]`, Dirichlet 0 | Función de Green | `greens_function_1d` |
| Helmholtz `Δu + k²u = f` | `[0, a] × [0, b]`, Dirichlet 0 | Expansión en autofunciones | `helmholtz_rect` |
| Telégrafo `u_tt + 2αu_t + βu = c²u_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `telegraph_sov` |
| Schrödinger pozo infinito `iℏψ_t = −ℏ²/(2m)ψ_xx` | `[0, L]`, Dirichlet 0 | Separación de variables | `schrodinger_well` |
| Schrödinger oscilador armónico `iℏψ_t = −ℏ²/(2m)ψ_xx + ½mω²x²ψ` | `x ∈ ℝ` | Hermite | `schrodinger_oscillator` |
| Schrödinger libre `iℏψ_t = −ℏ²/(2m)ψ_xx` | `x ∈ ℝ` | Transformada de Fourier / propagador libre | `schrodinger_free` |
| Transporte `u_t + c·u_x = 0` | `x ∈ ℝ` | Características | `characteristics_transport_1d` |
| Burgers no viscosa `u_t + u·u_x = 0` | `x ∈ ℝ` | Características generalizadas + Rankine-Hugoniot | `burgers_inviscid` |
| Biarmónica `EI u'''' = q(x)` | viga `[0, L]` apoyo simple | Expansión en senos | `biharmonic_beam` |
| **Cualquier EDP lineal 2°-orden** `A u_{ξ₁ξ₁} + B u_{ξ₁ξ₂} + C u_{ξ₂ξ₂} + … = 0` | dos variables | **Clasificador + forma canónica** (fallback) | `general_second_order` |

**245 tests backend + 32 tests frontend** (`pytest -v` / `npm test`) + smoke tests E2E con Playwright (`npm run test:e2e`). UI con switcher es/en. **Cada método del repertorio tiene
visualización**: superficies en `(x, t)` o `(x, y)`, gráficos 1D, o
cortes meridionales según la geometría.

Cada método produce la misma estructura de **10 pasos** (Paso 0–9):
planteamiento, clasificación, elección de método, desarrollo (incluyendo
los tres casos de λ cuando aplica), aplicación de BCs/ICs, solución
final, verificación simbólica, visualización y lectura física.

Lo que **NO** está todavía: armónicos esféricos completos (no
axisimétricos en la bola), expansión modal completa del tambor con
modos angulares $J_m \cos(m\theta)$, problemas con potencial $V(x)$
no nulo en Schrödinger. Tampoco: lenguaje natural (Fase 3), visión
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

### Despliegue en la nube

Para producción (Docker prod, Render.com, Vercel/Railway, VPS), ver
**[`DEPLOY.md`](./DEPLOY.md)**. Incluye:

- Multi-stage Dockerfiles (`docker/backend.prod.Dockerfile`, `docker/frontend.prod.Dockerfile`)
- `docker-compose.prod.yml` con healthcheck y nginx
- `render.yaml` para despliegue automático
- Configuración de CORS para el dominio público
- Checklist pre-despliegue

## Cómo probar los métodos

### Lenguaje natural

`POST /parse_natural` traduce un enunciado libre en español o inglés a
un `PDEProblem` canónico que después se manda a `/solve`:

```bash
curl -X POST http://localhost:8000/parse_natural \
  -H "Content-Type: application/json" \
  -d '{"text": "Resuelve la ecuación del calor en una barra de longitud L con extremos a temperatura cero y perfil inicial f(x) = sin(pi*x/L)."}'
```

La respuesta trae el `PDEProblem` parseado y un campo `source` que indica
si vino de la capa determinista o del LLM. El frontend muestra esta
estructura al usuario para confirmación antes de invocar al solver.

Para activar el clasificador Claude opcional (sólo necesario si los
patrones deterministas no cubren el enunciado), exporta:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Biblioteca

Guarda y consulta problemas resueltos en una base SQLite local:

```bash
# Guardar (después de un POST /solve)
curl -X POST http://localhost:8000/library \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi calor 1D favorito",
    "problem": { ... PDEProblem completo ... },
    "solution": { ... SolutionResponse completo ... },
    "source": "manual"
  }'

# Listar (con filtro opcional)
curl http://localhost:8000/library
curl "http://localhost:8000/library?equation_kind=heat"

# Recuperar / eliminar
curl http://localhost:8000/library/<id>
curl -X DELETE http://localhost:8000/library/<id>
```

La base se ubica en `backend/data/pdesolver.db` (configurable vía
`DATABASE_URL`). Los problemas que vinieron de imagen guardan la
miniatura como `image_data_url` para mostrarse en la cuadrícula de la
biblioteca.

### Imagen (foto, escaneo)

`POST /vision/extract` recibe una imagen (JPG/PNG/WEBP/HEIC) y devuelve
un `PDEProblem` canónico junto con la transcripción LaTeX y una
auto-evaluación de confianza:

```bash
curl -X POST http://localhost:8000/vision/extract \
  -F "file=@photo.jpg" \
  -F "hint=Es la ecuación del calor en una barra"
```

La respuesta incluye:
- `problem` — el `PDEProblem` canónico (igual que las otras dos vías).
- `transcribed_latex` — LaTeX verbatim, para que el usuario compare con
  la foto.
- `confidence` — `high`, `medium`, o `low`.
- `image_preview_data_url` — la imagen pre-procesada como data URL para
  renderizar en el navegador sin segunda llamada.

Requiere `ANTHROPIC_API_KEY`. Internamente: `claude-haiku-4-5` (vision)
con tool use + prompt caching del system prompt. PDFs todavía no son
soportados directamente; convierte cada página a JPG antes de subir
(`pdf2image` + Poppler).

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

### Laplace en disco

Dominio circular, dato en la circunferencia:

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{rr} + (1/r)*u_r + (1/r^2)*u_{\\theta\\theta} = 0",
  "equation_kind": "laplace",
  "geometry": "disk",
  "domain": {"x": ["0", "R"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "r=R", "value": "cos(theta)"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"R": "positive"}
}'
```

### Poisson 1D via función de Green

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "-u_{xx} = f(x)",
  "equation_kind": "poisson",
  "source_term": "x*(L - x)",
  "domain": {"x": ["0", "L"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"L": "positive"}
}'
```

### Helmholtz en rectángulo (con fuente)

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{xx} + u_{yy} + k^2*u = f",
  "equation_kind": "helmholtz",
  "source_term": "sin(pi*x/a)*sin(pi*y/b)",
  "domain": {"x": ["0", "a"], "y": ["0", "b"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=a", "value": "0"},
    {"type": "dirichlet", "where": "y=0", "value": "0"},
    {"type": "dirichlet", "where": "y=b", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"a": "positive", "b": "positive", "k": "positive"}
}'
```

### Ecuación del telégrafo

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{tt} + 2*alpha*u_t + beta*u = c^2*u_{xx}",
  "equation_kind": "telegraph",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [
    {"order": 0, "value": "sin(pi*x/L)"},
    {"order": 1, "value": "0"}
  ],
  "parameters": {"alpha": "positive", "beta": "nonnegative", "c": "positive", "L": "positive"}
}'
```

### Tambor circular (onda en disco axisimétrico)

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{tt} = c^2*(u_{rr} + u_r/r)",
  "equation_kind": "wave",
  "geometry": "disk",
  "domain": {"x": ["0", "R"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "r=R", "value": "0"}
  ],
  "initial_conditions": [
    {"order": 0, "value": "1 - (r/R)^2"},
    {"order": 1, "value": "0"}
  ],
  "parameters": {"R": "positive", "c": "positive"}
}'
```

### Calor en disco axisimétrico

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_t = alpha^2*(u_{rr} + u_r/r)",
  "equation_kind": "heat",
  "geometry": "disk",
  "domain": {"x": ["0", "R"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "r=R", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "1"}],
  "parameters": {"R": "positive", "alpha": "positive"}
}'
```

### Laplace en bola (axisimétrico, expansión multipolar)

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "\\nabla^2 u = 0",
  "equation_kind": "laplace",
  "geometry": "sphere",
  "domain": {"x": ["0", "R"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "r=R", "value": "cos(theta)"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"R": "positive"}
}'
```

### Schrödinger en pozo infinito

Partícula libre confinada en `[0, L]`:

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
  "equation_kind": "schrodinger",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "sqrt(2/L)*sin(pi*x/L)"}],
  "parameters": {"L": "positive", "hbar": "positive", "m": "positive"}
}'
```

### Transporte 1D por características

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_t + c*u_x = 0",
  "domain": {"x": ["-infty", "infty"], "t": ["0", "infty"]},
  "boundary_conditions": [],
  "initial_conditions": [{"order": 0, "value": "exp(-x^2)"}],
  "parameters": {"c": "positive"}
}'
```

### Viga simplemente apoyada (biarmónica 1D)

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "EI*u'\'''\'''\'''\'' = q(x)",
  "equation_kind": "biharmonic",
  "source_term": "sin(pi*x/L)",
  "domain": {"x": ["0", "L"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {"L": "positive", "EI": "positive"}
}'
```

### Laplace en semiplano (método de imágenes)

```bash
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{
  "equation_latex": "u_{xx} + u_{yy} = 0",
  "equation_kind": "laplace",
  "geometry": "halfplane",
  "domain": {"x": ["-infty", "infty"], "y": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "y=0", "value": "1/(1 + x^2)"}
  ],
  "initial_conditions": [{"order": 0, "value": "0"}],
  "parameters": {}
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

Las fases numeradas (1, 2-A, 2-B, 2-C, 2-D, 3, 4, 5) están todas
entregadas. Posibles extensiones sin fase numerada:

- **Visión avanzada**: soporte de PDF multipágina vía
  `pdf2image`+Poppler, backend pix2tex/Nougat para uso offline,
  soporte premium opcional Mathpix.
- **Solver avanzado**: armónicos esféricos completos, modos angulares
  del tambor, Schrödinger con $V \neq 0$, transformadas de Fourier y
  Laplace como métodos explícitos.
- **PDF server-side**: `/library/{id}/pdf` con WeasyPrint o Playwright
  para PDFs reproducibles sin pasar por el navegador.

## Licencia

Por definir.
