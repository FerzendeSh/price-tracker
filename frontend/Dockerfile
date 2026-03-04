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

# Copy the template (envsubst will resolve BACKEND_URL at runtime)
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copy built frontend
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# Nginx docker image auto-runs envsubst on /etc/nginx/templates/*.template
# We just need to set BACKEND_URL as an env var
CMD ["nginx", "-g", "daemon off;"]
