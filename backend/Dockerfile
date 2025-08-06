# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only requirements.txt first
COPY ./backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
# COPY ./backend/app .

# Create app directory and copy files
RUN mkdir -p /app/app
COPY ./backend/app/* /app/app/

# Create empty __init__.py if it doesn't exist
RUN touch /app/app/__init__.py

# Set Python path
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]