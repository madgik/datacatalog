# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Poetry
RUN pip install poetry

# Configure Poetry: disable the creation of virtual environments
RUN poetry config virtualenvs.create false

# Install project dependencies
RUN poetry install --no-dev

# Expose the port your app runs on
EXPOSE 8000

# Environment variables for Gunicorn to run your Flask app
ENV MODULE_NAME=data_quality_tool.controller
ENV VARIABLE_NAME=app
ENV PORT=8000

# Use the environment variable in the command
CMD ["sh", "-c", "poetry run gunicorn --bind 0.0.0.0:${PORT} controller:app"]
