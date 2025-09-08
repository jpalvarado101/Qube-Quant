# Build stage
FROM node:20 AS build
WORKDIR /app
# Copy manifests first for better Docker layer caching
COPY package.json package-lock.json* ./
# If a lockfile exists, use ci for reproducibility; otherwise fall back to install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
# Now copy the rest of the sources
COPY angular.json tsconfig.json tsconfig.app.json ./
COPY src ./src
# Build the app
RUN npm run build
# Serve stage
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend /usr/share/nginx/html
EXPOSE 80