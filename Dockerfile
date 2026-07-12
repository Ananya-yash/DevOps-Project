# Start from official slim Python 3.9 base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container first (before other files)
COPY requirements.txt .

# Run pip install to install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining project files into the container
COPY . .

# Expose port 5000 so the app is accessible from outside the container
EXPOSE 5000

# Set the startup command to run app.py
CMD ["python", "app.py"]
