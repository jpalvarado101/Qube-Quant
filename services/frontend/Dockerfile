# Stage 1: Build Angular app
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy all source files
COPY . .

# Build Angular production bundle
RUN npm run build -- --output-path=dist/frontend

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built Angular files from previous stage
COPY --from=build /app/dist/frontend /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
