# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory
COPY ./src ./src

# Copy data 
COPY ./data ./data

# Set environment variables for Flask
ENV FLASK_APP src.app
ENV FLASK_ENV development
ENV FLASK_DEBUG 1

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0"]
