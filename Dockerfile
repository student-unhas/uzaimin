# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir flask

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD [ "python", "app_real.py" ]
