# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install system dependencies for Adafruit_DHT (required for sensor libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir Adafruit_DHT --global-option=build_ext --global-option='--force-pi'

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD [ "python", "app_real.py" ]
