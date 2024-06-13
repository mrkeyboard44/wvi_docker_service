# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Environment variables for API token and MySQL credentials (to be passed at runtime)
ENV API_TOKEN=""
ENV MYSQL_USER=""
ENV MYSQL_PASSWORD=""
ENV MYSQL_HOST=""
ENV MYSQL_DATABASE=""

# Install cron
RUN apt-get update && apt-get -y install cron

# Copy cron job file to the cron.d directory
COPY crontab /etc/cron.d/cron-job

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron-job

# Apply cron job
RUN crontab /etc/cron.d/cron-job

# Run the command on container startup
#CMD cron && tail -f /var/log/cron.log

# TEST RUN PYTHON FILE
CMD ["python", "workiz-fetcher.py"]

