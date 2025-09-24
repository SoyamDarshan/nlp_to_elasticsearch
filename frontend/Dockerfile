FROM node:18-slim AS base
WORKDIR /app

# Install dependencies only when needed
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy the rest of the app
COPY . .

# Build the React app for production
RUN npm run build

# Use a lightweight web server for static files
FROM nginx:alpine
COPY --from=base /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
