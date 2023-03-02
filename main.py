import os
from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient, ASCENDING, DESCENDING
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
admin_db = get_DB('admin')
user_collection = accounts_db["users"]
post_collection = accounts_db["posts"]
secret_collection = admin_db["secrets"]

todaysDate = date.today().strftime("%m/%d/%y")

app = Flask(__name__)
default = None
app.secret_key = db_func.secretCreate()
@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("userHome", usr=user))
    else:
        return render_template("index.html", usr=default)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["signin_username"]
        password = request.form["signin_password"]
        user_data = user_collection.find_one({"Username": user})
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["Password"]):
            session["user"] = user
            return redirect(url_for("userHome", usr=user))
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
        bio = "This user hasn't updated their bio yet."
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = user_collection.find_one({"Username": user})
        if db_func.is_valid_email(email) == False:
            return  redirect(url_for("signup", usr=default, error="Not a valid Email address."))
        if user_data is not None:
            return  redirect(url_for("signup", usr=default, error="User already exists"))
        is_admin = False
        if user == "admin":
            is_admin = True
        new_user = schemas.newUser(user, hashed_password, email, is_admin, bio)
        user_collection.insert_one(new_user)
        return redirect(url_for("home", usr=user))
    else:
        return render_template("signup.html", usr=default)


@app.route("/<usr>/database")
def database(usr):
    if usr != "admin":
        return redirect(url_for("home", usr=default))
    else:
        return render_template("database.html")

@app.route("/<usr>/logout")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return render_template("logout.html")

@app.route("/profile/<usr>")
def userHome(usr):
    userPage = user_collection.find_one({"Username": usr})
    userPosts = post_collection.find({"Author": usr}).sort("date", DESCENDING).limit(5)
    postList = []
    for post in userPosts:
        if post["Author"] == usr:
            postList.append(post)
    if "user" in session:
        return render_template("profilePage.html", userPage=userPage, posts=postList, postLen=len(postList), currentUsr=session["user"])
    else:
        return render_template("profilePage.html", userPage=userPage, posts=postList, postLen=len(postList), currentUsr=default)
@app.route("/<usr>/profile/logout")
def profilelogout(usr):
    return redirect(url_for("logout_r", usr=usr))
    
@app.route("/<usr>/create-post", methods=["POST", "GET"])
def newpost(usr):
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]
        author = usr
        date = todaysDate
        post_id = db_func.generate_post_id()
        new_post = {
        '_id' : post_id,
        "Title" : title,
        "Content" : content,
        "Author" : author,
        "Date" : date,
        "Tags" : tags
        }
        schemas.newPost(title, content, author, todaysDate, tags, post_id)
        if db_func.tagsValid(tags) == False:
            return redirect(url_for("newpost", usr=usr, error="Invalid tags."))
        post_collection.insert_one(new_post)
        return redirect(url_for("viewpost", post_id=post_id))
    else:
        if "user" in session:
            return render_template("newPost.html", usr=usr)
        else:
            return redirect(url_for("login", usr=default))

@app.route("/<usr>/edit-profile", methods=["POST", "GET"])
def editProfile(usr):
    if request.method == "POST":
        newBio = request.form["bio"]
        newUsername = request.form["username"]
        newPassword = request.form["password"]
        passwordVerify = request.form["confirmPassword"]
        newEmail = request.form["email"]
        print(newUsername)
        UpdateResult = db_func.profileUpdate(newUsername, newEmail, newPassword, passwordVerify, usr, newBio, user_collection)
        if UpdateResult != "Success!":
            return redirect(url_for("editProfile", usr=usr, error=UpdateResult))
        else:
            session["user"] = newUsername
            return redirect(url_for("userHome", usr=usr))
    else:
        if "user" in session:
            return render_template("editProfile.html", usr=usr)
        else:
            return redirect(url_for("login", usr=default))
@app.route("/edit-profile")
def editRedirect():
    usr=session["user"]
    return redirect(url_for("editProfile", usr=usr))

@app.route("/post/<post_id>/=<usr>")
def viewpost(post_id, usr):
    try:
        current_post = post_collection.find_one({"_id": post_id})
        content = current_post["Content"]
        title = current_post["Title"]
        author = current_post["Author"]
        date = current_post["Date"]
        tags = current_post["Tags"]
    except OperationFailure:
        return render_template("404.html")
    if usr in session:
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, usr=usr)
    else:
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, usr=default)
@app.route("/post/logout")
def post_logout():
    return redirect(url_for("logout_r", usr=session["user"]))

@app.route("/<usr>/post/<post_id>")
def post_usrpage(usr, post_id):
    return redirect(url_for("viewpost", post_id=post_id, usr=usr))
@app.route("/post/<post_id>/<usr>")
def post_author(post_id, usr):
    return redirect(url_for("userHome", usr=usr))

@app.route("/<usr>/search", methods=["POST", "GET"])
def search(usr):
    return render_template("search.html", usr=usr)
@app.route("/profile/<usr>/search")
def search_profile(usr):
    return redirect(url_for("search", usr=usr))


if __name__ == "__main__":

    app.run(debug=True)