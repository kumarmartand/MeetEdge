FROM python:3.11-slim

# Install system dependencies including ffmpeg for audio and Dependencies for Playwright Chromium
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    gnupg \
    libgconf-2-4 \
    libxslt1.1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Default command (can be overridden by docker-compose, render.yaml, or railway.json)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
