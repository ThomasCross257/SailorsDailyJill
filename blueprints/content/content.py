from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort
import bcrypt
import libs.schemas as schemas
import libs.auth_func as au_func
import libs.content_func as cl_func
from datetime import date
from bson.objectid import ObjectId
from libs.globals import user_collection, post_collection, default, follow_collection
from pymongo.errors import OperationFailure
from app import app
from flask_wtf.csrf import validate_csrf, ValidationError
from libs.forms import BlogForm, EditProfileForm, SearchForm

content_bp = Blueprint('content', __name__, template_folder='templates', url_prefix="/content")

todaysDate = date.today().strftime("%m/%d/%y")

@content_bp.route("/profile/<usr>", methods=["GET", "POST"])
def userHome(usr):
    userPage = user_collection.find_one({"Username": usr})
    userPosts = post_collection.find({"Author": usr}).limit(5)
    postList = []
    for post in userPosts:
        if post["Author"] == usr:
            postList.append(post)
    postList = postList[::-1] 
    if "user" in session:
        isFollowing = cl_func.isFollowing(session["user"], usr)
        if request.method == "POST":
            followResult = cl_func.followUser(usr, session["user"])
            if "Success" in followResult:
                if isFollowing == True:
                    flash(f"You unfollowed {usr}.", "success")
                    return redirect(url_for("content.userHome", userPage=userPage, isFollowing=isFollowing, posts=postList, postLen=len(postList), currentUsr=session["user"], usr=usr))
                else:
                    flash(f"You followed {usr}.", "success")
                    return redirect(url_for("content.userHome", userPage=userPage, isFollowing=isFollowing, posts=postList, postLen=len(postList), currentUsr=session["user"], usr=usr))
            else:
                flash(followResult)
                return redirect(url_for("content.userHome", userPage=userPage, isFollowing=isFollowing, posts=postList, postLen=len(postList), currentUsr=session["user"], usr=usr))
        else:
            return render_template("profilePage.html", userPage=userPage, isFollowing=isFollowing, posts=postList, postLen=len(postList), currentUsr=session["user"], usr=usr)
    else:
        return render_template("profilePage.html", userPage=userPage, posts=postList, postLen=len(postList), currentUsr=default)
    
@content_bp.route("/profile/create-post/<usr>", methods=["POST", "GET"])
def newpost(usr):
    form = BlogForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                abort(400, 'Invalid CSRF token')
            title = form.title.data
            content = form.content.data
            tags = form.tags.data
            author = usr
            post_id = cl_func.generate_post_id()
            new_post = schemas.newPost(title, content, author, todaysDate, tags, post_id)
            if cl_func.tagsValid(tags) == False:
                return redirect(url_for("content.newpost", usr=usr, error="Invalid tags.", currentUsr=session["user"]))
            post_collection.insert_one(new_post)
            return redirect(url_for("content.viewpost", post_id=post_id, usr=usr, currentUsr=session["user"]))
    else:
        if "user" in session:
            return render_template("newPost.html", usr=usr, currentUser=session["user"], form=form)
        else:
            return redirect(url_for("auth.login", usr=default))

@content_bp.route("/profile/edit-profile/<usr>", methods=["POST", "GET"])
def editProfile(usr):
    user = user_collection.find_one({'Username': usr})
    if request.method == "POST":
        newBio = request.form["bio"]
        newUsername = request.form["username"]
        newPassword = request.form["password"]
        passwordVerify = request.form["confirmPassword"]
        newEmail = request.form["email"]
        profilePic = request.form["profilePic"]
        if newUsername:
            if au_func.usernameExists(newUsername, user_collection) == True:
                return redirect(url_for("editProfile", usr=usr, error="Username already exists."))
            elif newUsername == usr:
                return redirect(url_for("editProfile", usr=usr, error="Username is the same as the current one."))
            else:
                user_collection.update_one({'_id': ObjectId(user["_id"])}, {'$set': {'Username': newUsername}})

        if newBio:
            user_collection.update_one({'_id': ObjectId(user["_id"])}, {'$set': {'Biography': newBio}})

        if newPassword and passwordVerify:
            if newUsername == newPassword:
                hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())
                user_collection.update_one({'_id': ObjectId(user.get_id())}, {'$set': {'Password': hashed_password}})
            else:
                return redirect (url_for("content.editProfile", usr=usr, error="Passwords do not match."))
        if newEmail:
            if au_func.is_valid_email(newEmail) == False:
                return redirect(url_for("content.editProfile", usr=usr, error="Not a valid Email address."));
            else:
                user_collection.update_one({'_id': ObjectId(user["_id"])}, {'$set': {'Email address': newEmail}})
        return redirect(url_for("content.userHome", usr=usr))
        
    else:
        if "user" in session and usr == session["user"]:
            return render_template("editProfile.html", usr=usr, currentUsr=session["user"])
        else:
            return redirect(url_for("login", usr=default, currentUsr=default))
@content_bp.route("/edit-profile")
def editRedirect():
    usr=session["user"]
    return redirect(url_for("editProfile", usr=usr))

@content_bp.route("/post/<post_id>/=<usr>")
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
    if "user" in session:
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, currentUser=session["user"])
    else:
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, currentUser=default)
@content_bp.route("/post/logout")
def post_logout():
    return redirect(url_for("content.logout_r", usr=session["user"]))

@content_bp.route("/<usr>/post/<post_id>")
def post_usrpage(usr, post_id):
    return redirect(url_for("content.viewpost", post_id=post_id, usr=usr, currentUser=session["user"]))
@content_bp.route("/post/<post_id>/<usr>")
def post_author(post_id, usr):
    return redirect(url_for("content.userHome", usr=usr, currentUser=session["user"]))

@content_bp.route("/profile/<usr>/post/<post_id>")
def post_archive(usr, post_id):
    return redirect(url_for("content.viewpost", post_id=post_id, usr=usr, currentUser=session["user"]))

@content_bp.route("/search/<usr>", methods=["POST", "GET"])
def search(usr):
    if request.method == "POST":
        search = request.form["search"]
        if cl_func.searchValid(search) == False:
            return redirect(url_for("content.search", usr=usr, error="Invalid search.", currentUser=session["user"], search=None))
        else:
            search = cl_func.searchPosts(search)
            print(search)
            search = search[::-1]
            return render_template("search.html", usr=usr, currentUser=session["user"], search=search)
    else:
        if "user" in session:
            return render_template("search.html", usr=usr, currentUser=session["user"], search=None)
        else:
            return redirect(url_for("auth.login", usr=default, currentUsr=default))
@content_bp.route("/profile/search/<usr>")
def search_profile(usr):
    return redirect(url_for("content.search", usr=usr, currentUser=session["user"]))
@content_bp.route("/search/search")
def doubleSearch(usr):
    return redirect(url_for("content.search", usr=usr, currentUser=session["user"]))

@content_bp.route("/profile/<usr>/archive")
def archive(usr):
    userPage = user_collection.find_one({"Username": usr})
    userPosts = post_collection.find({"Author": usr})
    postList = []
    for post in userPosts:
        if post["Author"] == usr:
            postList.append(post)
    postList = postList[::-1]
    if "user" in session == True:
        return render_template("archive.html", usr=usr, posts=postList, postLen=len(postList), userPage=userPage, currentUser=session["user"])
    else:
        return render_template("archive.html", usr=usr, posts=postList, postLen=len(postList), userPage=userPage, currentUser=default)
    
@content_bp.route("/feed/<currentUsr>")
def feed(currentUsr):
    if "user" in session:
        following = follow_collection.find({"Username": session["user"]})
        postList = []
        followList = []
        for user in following:
            followList.extend(user["Following"])
        for user in followList:
            userPosts = post_collection.find({"Author": user})
            for post in userPosts:
                postList.append(post)
        postList = postList[::-1]
        return render_template("feed.html", currentUsr=session["user"], posts=postList, postLen=len(postList))

    else:
        return redirect(url_for("auth.login", usr=default, currentUsr=default))