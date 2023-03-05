# SailorsDailyJill

<div>
    <h1 align='center'>
        <br>
        <img src ="static/img/ApplicationLogo.png" alt=Bottle with a Compass inside>
        <br>
        Sailor's Daily Jill
        <h2 align='center'>Providing the navigation for your daily needs.</h2>
    </h1>
</div>
<br>
<h1>What is Sailor's Daily Jill?</h1>
Taking inspiration from sailing terminologies, a "Jill" is a measurement of liquid, particularly used to describe rum. For, what's a sailor to do without their daily jill of rum or grog?
<br>
This project aims to fuilfil your daily needs with a flask-basked template that can easily dockerized and managed via kubernetes.
<hr>
<h1>Features</h1>
* Flask application with login and signup functionality.
* Blog posting capabilities.
* Query the database by searching for posts made by other users
* Use the Admin dashboard to create and remove users as will with a simple, friendly interface
* Mobile support via boostrap
<h2>Future features</h2>
* Profile pictures
* Kubernetes Integration
* Verification methods like 2FA
* Redesign and support for color schemes
* And much more!
<h1>Installation</h1>
This repo supports two methods of running and building the application.
<br>
The first of which is via docker, and the second of which is by running this app locally.
<hr>
<h2>Local Install</h2>
Clone this repository with the following statement.

```bash
git clone https://github.com/ThomasCross257/SailorsDailyJill.git
```
Enter the folder where your repository was cloned to and simply run

```bash
flask --app main run
```
You should get an output stating what IP it's running on on a local development server.
<hr>
<h2>Docker Install</h2>
Clone this repository much like the local install.

```bash
git clone https://github.com/ThomasCross257/SailorsDailyJill.git
```

Create a Dockerfile with the following:
```docker
# Base image. Change the image as you see fit
FROM python:3.9

# Set working directory
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV MONGO_URI= <your mongo URI>

CMD ["flask", "run", "--host", "0.0.0.0"]
```
Then run the following
```docker
docker run -p 5000:5000 sailorsdailyjill
```