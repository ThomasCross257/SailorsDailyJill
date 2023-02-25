import os
from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient
from dotenv import load_dotenv
from pandas import DataFrame
import bcrypt
from db_func import is_valid_email as emailValid #Should move personal library to another directory later

load_dotenv()

def get_DB(DB_NAME):
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

# Database queries for global definitions begins here

# Account collection
accounts_db = get_DB('accounts')
user_collection = accounts_db["users"]

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
default = None

@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("userLogin", usr=user))
    else:
        return render_template("index.html", usr=default)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["signin_username"]
        password = request.form["signin_password"]
        user_data = user_collection.find_one({"Username": user})
        # DEBUG: print(bcrypt.checkpw(password.encode('utf-8'), user_data["Password"])) Should return true or false
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["Password"]):
            session["user"] = user
            return redirect(url_for("userLogin", usr=user))
        else:
            return  redirect(url_for("login", usr=default, error="Invalid Login Information."))
    else:
        return render_template("login.html", usr=default)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["signup_user"]
        password = request.form["signup_password"]
        email = request.form["signup_email"]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = user_collection.find_one({"Username": user})
        if emailValid(email) == False:
            return  redirect(url_for("signup", usr=default, error="Not a valid Email address."))
        if user_data is not None:
            return  redirect(url_for("signup", usr=default, error="User already exists"))

        new_user = {
            "Username" : user,
            "Password" : hashed_password,
            "Email address" : email,
            "Admin" : False
        }
        user_collection.insert_one(new_user)
        return redirect(url_for("userLogin", usr=user))
    else:
        return render_template("signup.html", usr=default)


@app.route("/database")
def database():
    return render_template("database.html")

@app.route("/<usr>/logout")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return render_template("logout.html")

@app.route("/<usr>/home")
def userLogin(usr):
    if "user" in session:
        user = session["user"]
        print(user)
        return render_template("profilePage.html", username = usr)
    else:
        return render_template("login.html", usr=default)

if __name__ == "__main__":

    app.run(debug=True)