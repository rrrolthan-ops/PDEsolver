# Multi-stage production build for the frontend.
# Stage 1: build the static bundle with Node.
# Stage 2: serve it with nginx (tiny image, ~25 MB).

FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first to make `npm ci` cache-friendly.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Now the source.
COPY . .

# The build picks up VITE_API_BASE_URL from the environment, so set it
# before `docker build` (e.g. with --build-arg) or before running the
# stack. Default to the same-host backend.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# ---------------------------------------------------------------------
# Stage 2: serve the dist/ folder.
# ---------------------------------------------------------------------
FROM nginx:1.27-alpine

# Copy a minimal nginx config that serves the SPA and falls back to
# index.html for client-side routing.
COPY --from=builder /app/dist /usr/share/nginx/html
RUN printf '%s\n' \
    'server {' \
    '  listen 80;' \
    '  server_name _;' \
    '  root /usr/share/nginx/html;' \
    '  index index.html;' \
    '  location / {' \
    '    try_files $uri $uri/ /index.html;' \
    '  }' \
    '  # Long-cache hashed assets, no-cache the entry HTML.' \
    '  location ~* \.(?:js|css|woff2?|ttf|png|jpg|svg)$ {' \
    '    expires 30d;' \
    '    add_header Cache-Control "public, immutable";' \
    '  }' \
    '  location = /index.html {' \
    '    add_header Cache-Control "no-cache, no-store, must-revalidate";' \
    '  }' \
    '}' \
    > /etc/nginx/conf.d/default.conf

EXPOSE 80

# Run as the standard nginx user (already configured in the base image).
CMD ["nginx", "-g", "daemon off;"]
