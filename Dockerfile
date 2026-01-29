# Use Python base image
FROM python:3.12-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy web folder and build React
COPY web/package*.json ./web/
RUN cd web && npm install

COPY web/ ./web/
RUN cd web && npm run build

# Copy the rest of the application
COPY . .

# Railway provides PORT env var
ENV PORT=8080
EXPOSE 8080

# Start command with explicit shell
CMD ["/bin/sh", "-c", "gunicorn api.server:app --bind 0.0.0.0:${PORT}"]
