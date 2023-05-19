# Start from the official Python 3.11 image
FROM python:3.11-slim

# Set the working directory to /opt/app
WORKDIR /opt/app
ENV PYTHONPATH="/opt/app/src"

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Start the application using uvicorn
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000", "--logging-config", "logging_config.json"]
