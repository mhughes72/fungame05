FROM python:3.11-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install JS dependencies and build frontend (separate layer for caching)
COPY web/package.json web/package-lock.json* web/
RUN cd web && npm install

COPY web/ web/
RUN cd web && npm run build

# Copy application source
COPY . .

ENV PORT=8080
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
