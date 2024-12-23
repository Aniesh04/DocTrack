# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml

# Install Poetry (if using pyproject.toml)
RUN pip install poetry

# Install system dependencies required by some packages
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && apt-get clean

# Install Python dependencies
RUN poetry install --no-dev || pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the command to start the application
CMD ["hypercorn", "main:app", "--bind", "[::]:8000"]
