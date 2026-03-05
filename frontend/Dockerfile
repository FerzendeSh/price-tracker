# ── Build stage ──
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# VITE_API_URL is empty for production (Nginx reverse-proxies to backend)
ENV VITE_API_URL=""
RUN npm run build

# ── Production stage ──
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy the template (envsubst resolves PORT + BACKEND_URL at runtime)
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Copy built frontend
COPY --from=build /app/dist /usr/share/nginx/html

# Default PORT for local docker-compose; Render overrides with its own
ENV PORT=80

EXPOSE 80

# Only substitute PORT and BACKEND_URL — leave nginx vars ($uri, $host, etc.) alone
CMD ["/bin/sh", "-c", "envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
