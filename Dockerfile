# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and poetry.lock (if available) to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies using Poetry
RUN poetry install --no-root

# Copy the rest of the application code to the container
COPY . /app

# Expose the application port (for FastAPI)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Start the application with hypercorn
CMD ["hypercorn", "main:app", "--bind", "[::]:$PORT"]
