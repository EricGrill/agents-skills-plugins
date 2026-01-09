FROM python:3.11-slim

WORKDIR /app

# Copy deployment files
COPY deployment/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run the web server
CMD ["python", "-m", "web_server"]
