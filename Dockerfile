# Base image. Change the image as you see fit
FROM python:3.9

# Set working directory
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV MONGO_URI=/app/mongo_uri.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
