# Python API Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8002"]

