FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código backend
COPY ../../autonomy /app/autonomy
COPY ../../blockchain /app/blockchain
COPY matverse_operator.py /app/

# User não-root
RUN useradd -m -u 1000 operator
USER operator

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

CMD ["kopf", "run", "--standalone", "/app/matverse_operator.py"]
