# Base image: lightweight Python 3.9
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (layer caching: only re-runs if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and config/data files
COPY run.py config_utils.py data_utils.py signal_utils.py metrics_utils.py ./
COPY config.yaml data.csv ./

# Default command: run the batch job with all required arguments
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]
