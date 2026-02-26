# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run uvicorn when the container launches
# Use 0.0.0.0 for host to be accessible from outside
# Use port defined by PORT environment variable (Cloud Run requirement) or default to 8080
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
