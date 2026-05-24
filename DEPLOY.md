# Despliegue

Esta guía cubre tres escenarios:

1. **Local de desarrollo** (sin contenedores): backend con `uvicorn`, frontend con `vite`.
2. **Local con Docker** (producción simulada): backend + nginx con `docker compose -f docker-compose.prod.yml`.
3. **Nube (Render.com)**: despliegue automático desde GitHub usando `render.yaml`.

---

## 1. Local de desarrollo

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate     # o `.venv\Scripts\activate` en Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. El frontend se comunica con `http://localhost:8000`.

Variables de entorno opcionales para el backend:

| Variable             | Por defecto                      | Descripción |
|----------------------|----------------------------------|-------------|
| `ANTHROPIC_API_KEY`  | *(vacía)*                        | Necesaria sólo para los modos "lenguaje natural" y "visión" (entrada por imagen). Las pruebas y el modo manual funcionan sin ella. |
| `DATABASE_URL`       | `sqlite:///./data/pdesolver.db` | Ruta a la base de datos SQLite de la biblioteca. |

---

## 2. Local con Docker

### Dev (hot-reload, monta el código)

```bash
docker compose up --build
# Backend en :8000, frontend (Vite dev) en :5173
```

### Producción simulada (bundle estático + nginx)

```bash
# Construye con la URL del backend que verá el usuario (en local: localhost:8000).
VITE_API_BASE_URL=http://localhost:8000 docker compose -f docker-compose.prod.yml up --build -d
```

Esto sirve el frontend compilado en `:80` y el backend FastAPI en `:8000`. Diferencias respecto al stack de dev:

- Multi-stage builds — la imagen final del frontend pesa ~30 MB (nginx + dist).
- El backend corre como usuario no-root.
- Healthcheck en `/health`; el frontend espera a que el backend esté saludable antes de arrancar.
- Sin montaje de código fuente: las imágenes son auto-contenidas.

Para detener y limpiar volúmenes:

```bash
docker compose -f docker-compose.prod.yml down -v
```

---

## 3. Render.com (gratis para demos)

El repo trae un `render.yaml` listo para usar:

1. **Crea un Blueprint en Render**: dashboard → New → Blueprint → conecta el repo.
2. **Render detecta `render.yaml`** y propone dos servicios:
   - `pdesolver-backend` (Python web service, plan free).
   - `pdesolver-frontend` (Static site, plan free).
3. **Configura los secretos** en el dashboard antes de desplegar:
   - `ANTHROPIC_API_KEY` (sólo si quieres habilitar lenguaje natural + visión).
4. **Apply**: Render construye ambos servicios y los enlaza. El frontend pickea automáticamente la URL pública del backend vía la directiva `fromService`.

Notas:

- El plan free duerme tras 15 min de inactividad. La primera petición tras dormir tarda ~30 s en despertar el backend.
- El disco persistente (`1 GB`) guarda la base SQLite de la biblioteca.
- Para upgradear: cambia `plan: free` → `plan: starter` en `render.yaml` y re-aplica el blueprint.

### Alternativas equivalentes

- **Railway / Fly.io**: misma idea, distintas etiquetas. Usa `docker-compose.prod.yml` como referencia.
- **Vercel + Railway**: Vercel para el frontend (estático), Railway para el backend Python.
- **VPS propio**: clona, `docker compose -f docker-compose.prod.yml up -d` detrás de un Caddy o nginx reverse-proxy para HTTPS.

---

## CORS

`backend/app/main.py` permite por defecto `localhost:5173` y `127.0.0.1:5173`. En producción, edita la lista `allow_origins` para añadir el dominio público del frontend:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://pdesolver-frontend.onrender.com",  # ← añadir aquí
    ],
    ...
)
```

O usa una variable de entorno (recomendado):

```python
import os
origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
```

---

## Diagnóstico

| Síntoma                             | Probable causa                        | Arreglo |
|-------------------------------------|---------------------------------------|---------|
| Frontend muestra "Failed to fetch"  | `VITE_API_BASE_URL` apunta al lugar incorrecto, o CORS bloquea | Verifica la URL del backend; añade el dominio frontend a CORS. |
| `/parse/natural` o `/vision` falla con 503 | `ANTHROPIC_API_KEY` no configurada    | Configúrala en el entorno o usa el modo manual. |
| Render free tier "Application failed" | El plan free tiene 512 MB RAM; SymPy puede consumir más | Sube a `starter` (1 GB+). |
| Tests CI fallan localmente con éxito | Distinto Python / Node                | El CI usa Python 3.11/3.12 y Node 20 — alinea localmente. |
| `pytest` cuelga >5 min               | Es normal: el Schrödinger libre y Duhamel hacen convoluciones complejas | Espera o lanza un subconjunto: `pytest tests/solver -k "not schrod and not duhamel"`. |

---

## Checklist pre-despliegue

- [ ] `cd backend && pytest -q` — los 245 tests deben pasar.
- [ ] `cd frontend && npm test` — los 23 tests deben pasar.
- [ ] `cd frontend && npx tsc -b --noEmit` — sin errores de tipos.
- [ ] `cd backend && ruff check app tests` — sin warnings.
- [ ] CORS configurado para el dominio frontend público.
- [ ] `ANTHROPIC_API_KEY` configurada en el dashboard (si quieres modos NL + visión).
- [ ] Disco persistente configurado (para la biblioteca SQLite).
