FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Quarantine directory for uploaded samples (no public access)
RUN mkdir -p uploads && chmod 700 uploads

EXPOSE 4173

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:4173/health', timeout=3)"

CMD ["python", "server.py"]
