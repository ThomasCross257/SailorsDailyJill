import os
from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv
from pandas import DataFrame
import bcrypt
import libs.schemas as schemas
from datetime import date
import libs.db_func as db_func

load_dotenv()

def get_DB(DB_NAME):
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

# Database queries for global definitions begins here

# Account collection
accounts_db = get_DB('accounts')
user_collection = accounts_db["users"]
post_collection = accounts_db["posts"]

todaysDate = date.today().strftime("%m/%d/%y")

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
        if db_func.emailValid(email) == False:
            return  redirect(url_for("signup", usr=default, error="Not a valid Email address."))
        if user_data is not None:
            return  redirect(url_for("signup", usr=default, error="User already exists"))
        new_user = schemas.newUser(user, hashed_password, email, False)
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
@app.route("/<usr>/create-post", methods=["POST", "GET"])
def newpost(usr):
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]
        author = usr
        post_id = db_func.generate_post_id()
        print(title)
        print(content)
        print(tags)
        print(author)
        print(post_id)
        new_post = {
        '_id' : post_id,
        "Title" : title,
        "Content" : content,
        "Author" : author,
        "Date" : date,
        "Tags" : tags
        }
        print (new_post)
        """
        schemas.newPost(title, content, author, todaysDate, tags, post_id)
        if db_func.tagsValid(tags) == False:
            return redirect(url_for("newpost", usr=usr, error="Invalid tags."))
        """
        post_collection.insert_one(new_post)
        return render_template("newPost.html", post=new_post)
    else:
        return render_template("newPost.html", post=default)
@app.route("/<post>")
def viewpost(post):
    try:
        post = post_collection.find_one({"_id": post})
        content = post["Content"]
        title = post["Title"]
        author = post["Author"]
        date = post["Date"]
        tags = post["Tags"]
    except OperationFailure:
        return render_template("404.html")
    return render_template("blogPost.html", content, title, author, date, tags)

if __name__ == "__main__":

    app.run(debug=True)