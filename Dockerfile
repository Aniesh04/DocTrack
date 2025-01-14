# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system-level dependencies for mysqlclient and others
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . /app

# Create and activate a virtual environment, then install Python dependencies
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose the application port
EXPOSE 8000

# Set the default command to run the application
CMD ["/opt/venv/bin/hypercorn", "main:app", "--bind", "0.0.0.0:8000"]
