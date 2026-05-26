FROM python:3.12-slim

# Create non-root user for OpenShift compatibility
RUN useradd -m -u 1001 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py models.py ./

# Switch to non-root user
USER 1001

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
