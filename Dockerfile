# Base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port used by the Flask app
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Start the Flask app
CMD ["flask", "run", "--host", "0.0.0.0"]