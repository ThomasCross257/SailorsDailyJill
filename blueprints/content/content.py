from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort, send_file
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
from werkzeug.utils import secure_filename
import os

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
                redirect (url_for("errors.errorhandler(400)", usr=usr, currentUsr=session["user"]))
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
            return render_template("makePost.html", usr=usr, currentUser=session["user"], form=form, editMode=False)
        else:
            return redirect(url_for("auth.login", usr=default))

@content_bp.route("/profile/edit-profile/<usr>", methods=["POST", "GET"])
def editProfile(usr):
    user = user_collection.find_one({'Username': usr})
    form = EditProfileForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                abort(400, 'Invalid CSRF token')

            # check if user has entered a new username and if it is not already taken
            if form.username.data and form.username.data != user["Username"] and cl_func.validUsernameLen(form.username.data):
                if user_collection.find_one({"Username": form.username.data}) is not None:
                    flash("Username already exists.", "error")
                    return redirect(url_for("content.editProfile", usr=usr))
                else:
                    user["Username"] = form.username.data

            # check if user has entered a new bio
            if form.bio.data and form.bio.data != user["Biography"] and cl_func.validBioLen(form.bio.data):
                user["Biography"] = form.bio.data

            # check if user has uploaded a new profile picture
            if form.profilePic.raw_data:
                # save the uploaded file to the server
                filename = secure_filename(form.profilePic.data.filename)
                basename, extension = os.path.splitext(filename)
                basename = "pfp"
                filename = f"{basename}-{user['Username']}{extension}"
                file_path = os.path.join(app.root_path, 'static', 'uploads', str(user["_id"]),'profile', filename)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                form.profilePic.data.save(file_path)    
                # update the user's profile picture in the database
                user["Profile Picture"] = "uploads/" + str(user["_id"]) + "/pfp/" + filename

            # check if user has entered a password to confirm changes
            if form.passwordConf.data:
                if bcrypt.checkpw(form.passwordConf.data.encode('utf-8'), user["Password"]):
                    user_collection.update_one({"_id": user["_id"]}, {"$set": user})
                    flash("Profile updated successfully!", "success")
                    return redirect(url_for("content.userHome", usr=user["Username"]))
                else:
                    flash("Passwords do not match.", "error")
                    return redirect(url_for("content.editProfile", usr=usr))
            else:
                flash("Please enter your password to confirm changes.", "error")
                return redirect(url_for("content.editProfile", usr=usr))
    return render_template("editProfile.html", form=form, usr=usr, user=user)



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
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, currentUser=session["user"], post_id=post_id)
    else:
        return render_template("blogPost.html", content=content, title=title, author=author, date=date, tags=tags, currentUser=default)
@content_bp.route("/post/<post_id>/edit=<usr>", methods=["POST", "GET"])
def editpost(post_id, usr):
    form = BlogForm()
    post = post_collection.find_one({"_id": post_id})
    return render_template("makePost.html", usr=usr, currentUser=session["user"], form=form, editMode=True, post_id=post_id, post=post)

@content_bp.route("/search/<usr>", methods=["POST", "GET"])
def search(usr):
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            validate_csrf(form.csrf_token.data, app.secret_key)
        except ValidationError:
            abort(400, 'Invalid CSRF token')
        search = form.search.data
        if cl_func.searchValid(search) == False:
            return redirect(url_for("content.search", usr=usr, error="Invalid search.", currentUser=session["user"], search=None, form=form))
        else:
            search = cl_func.searchPosts(search)
            search = search[::-1]
            return render_template("search.html", usr=usr, currentUser=session["user"], search=search, form=form)
    else:
        if "user" in session:
            return render_template("search.html", usr=usr, currentUser=session["user"], search=None, form=form)
        else:
            return redirect(url_for("auth.login", usr=default, currentUsr=default))

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
"""
@app.route('/uploads/<userid>/pfp/<filename>')
def uploaded_file(userid, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], userid, 'pfp', filename)
    return send_file(file_path, mimetype='image/jpeg')
"""

@app.route('/uploads/<userid>/pfp/<filename>')
def uploaded_pfp(userid, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], userid, 'pfp', filename)
    return send_file(file_path, mimetype='image/jpeg')