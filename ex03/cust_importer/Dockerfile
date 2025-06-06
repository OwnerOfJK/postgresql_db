FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir pandas psycopg2-binary

# Default command
CMD ["python3", "automatic_table.py"]
