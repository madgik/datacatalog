# Use the official Nginx image from Docker Hub
FROM nginx:alpine

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend build files to nginx default public folder
COPY . /usr/share/nginx/html/

# Expose port 80
EXPOSE 80