# Multi-stage image: build the React app, then serve it with Nginx and
# reverse-proxy API/admin requests to the Django backend.
# Build context is the repository root (see docker-compose.prod.yml).

# --- Stage 1: build the React frontend ---
FROM node:22 AS build

WORKDIR /app

COPY frontend/react/package*.json ./
RUN npm install

COPY frontend/react/ ./

# Same-origin API: requests go to /api/ and Nginx proxies them to the backend.
ENV VITE_API_URL=/api/
RUN npm run build

# --- Stage 2: Nginx serving the build + reverse proxy ---
FROM nginx:stable

# Static SPA build.
COPY --from=build /app/dist /usr/share/nginx/html

# Config template: ${DOMAIN} is substituted at container start from the
# environment (official nginx image processes /etc/nginx/templates/*.template).
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80 443
