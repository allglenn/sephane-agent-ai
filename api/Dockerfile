FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for chromadb and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python packages including development tools
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir flask-debug watchdog

# Copy the rest of the application
COPY . .

# Make sure the environment file is loaded
ENV $(cat .env | xargs)
ENV PORT=5001

# Use flask run with reload enabled using PORT env variable
CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=${PORT} --reload"]
