# Use Python 3.10 as base image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "app.py"]
