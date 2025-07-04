FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY k8s_async_version.py .

# Run with Uvicorn
CMD ["uvicorn", "k8s_async_version:app", "--host", "0.0.0.0", "--port", "8000"]
