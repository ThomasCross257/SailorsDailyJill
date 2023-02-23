import os
from flask import Flask, redirect, url_for, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
from pandas import DataFrame
import bcrypt

def get_DB(DB_NAME):
    load_dotenv()
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

# Database queries for global definitions begins here

# Account collection
accounts_db = get_DB('accounts')
user_collection = accounts_db["users"]

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["signin_username"]
        password = request.form["signin_password"]
        user_data = user_collection.find_one({"Username": user})
        # DEBUG: print(bcrypt.checkpw(password.encode('utf-8'), user_data["Password"])) Should return true or false
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["Password"]):
            return redirect(url_for("userLogin", usr=user))
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["signup_user"]
        password = request.form["signup_password"]
        email = request.form["signup_email"]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = {
            "Username" : user,
            "Password" : hashed_password,
            "Email address" : email,
            "Verified" : False,
            "Admin" : False
        }
        user_data = user_collection.find_one({"Username": user})
        if user == user_data["Username"]:
            return render_template("signup.html", error="User already exists")
        else:
            user_collection.insert_one(new_user)
            return redirect(url_for("usr_verification", usr=user))
    else:
        return render_template("signup.html")

@app.route("/database")
def database():
    return render_template("database.html")

@app.route("/redirect")
def logout_r():
    return render_template("redirect.html")

@app.route("/<usr>/home")
def userLogin(usr):
    return render_template("userpage.html")

@app.route("/verification")
def usr_verification(usr):
    return render_template("verification.html")

if __name__ == "__main__":

    app.run(debug=True)