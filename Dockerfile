FROM python:latest

WORKDIR /SDL-docker

COPY main.py /SDL-docker/main.py

COPY templates /SDL-docker/templates

COPY static /SDL-docker/static

COPY requirements.txt /SDL-docker/requirements.txt

COPY .env /SDL-docker/.env

RUN pip install /SDL-docker/requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
