FROM python:3.13-alpine

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apk --no-cache add curl

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]