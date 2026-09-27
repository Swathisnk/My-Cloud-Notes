# Use standard, slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workspace directory
WORKDIR /app

# Install system dependencies (build-essential for gunicorn/pillow if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies list and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose Django port
EXPOSE 8000

# Shell command: run migrations, collect static, and spin up production gunicorn WSGI server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn cloudnote.wsgi:application --bind 0.0.0.0:8000"]
