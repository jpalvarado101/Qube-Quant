# Build stage
FROM node:20 AS build
WORKDIR /app
COPY package.json angular.json tsconfig.json ./
COPY src ./src
RUN npm ci && npm run build


# Serve stage
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend /usr/share/nginx/html
EXPOSE 80