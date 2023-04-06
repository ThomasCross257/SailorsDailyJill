from flask import Blueprint, render_template, redirect, url_for, request, session, url_for, flash
import libs.admin_func as admin_func
import libs.auth_func as auth_func
import libs.content_func as cl_func
from libs.globals import user_collection, post_collection, default
from libs.forms import EditUserForm, RegisterForm, SearchForm, DeleteForm
from flask_wtf.csrf import validate_csrf, ValidationError
from app import app

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix="/admin")

@admin_bp.route("/database/<usr>")
def database(usr):
    form = SearchForm()
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        userList = []
        for user in user_collection.find():
            userList.append(user)        
        return render_template("database.html", usr=session["user"], userList=userList, currentUsr=session["user"], form=form)

@admin_bp.route("/database/newEntry/<usr>", methods=["GET", "POST"])
def newEntry(usr):
    form = RegisterForm()
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    if request.method == "POST" and form.validate_on_submit():
        try:
            validate_csrf(form.csrf_token.data, app.secret_key)
        except ValidationError:
            return redirect(url_for("error_bp.errorhandler(400)", usr=session["user"], error="Invalid CSRF token."))
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password_conf = form.passwordConf.data
        adminTxt = form.admin.data

        # Call the create_user function
        result = auth_func.registerAccount(username, email, password, password_conf, adminTxt)

        if result.startswith("Error"):
            # If there was an error, redirect to newEntry with an error message
            return redirect(url_for("admin.newEntry", usr=session["user"], error=result))
        else:
            # If successful, redirect to database
            return redirect(url_for("admin.database", usr=session["user"]))
    else:
        return render_template("newEntry.html", usr=session["user"], form=form)

@admin_bp.route("/database/editEntry/<usr>/<usrEdit>", methods=["GET", "POST"])
def editEntry(usr, usrEdit):
    User = user_collection.find_one({"Username": usrEdit})
    form = EditUserForm(User)
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        if request.method == "POST" and form.validate_on_submit():
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                return redirect(url_for("error_bp.errorhandler(400)", usr=session["user"], error="Invalid CSRF token."))
            username = form.username.data
            email = form.email.data
            password = form.password.data
            passwordConf = form.passwordConf.data
            admin = form.admin.data
            profilePic = form.profilePic.data
            return admin_func.update_user(usrEdit, username, email, password, passwordConf, admin, profilePic)
        else:
            print(User)
            return render_template("editEntry.html", usr=session["user"], User=User, form=form)

@admin_bp.route("/content/profile/database/<usr>")
def database_route(usr):
    return redirect(url_for("admin.database", usr=session["user"]))

@admin_bp.route("/database/deleteEntry/<usr>/<usrDelete>", methods=["POST"])
def deleteEntry(usr, usrDelete, methods=["POST", "GET"]):
    form = DeleteForm()
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        if request.method == "POST" and form.validate_on_submit():
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                return redirect(url_for("error_bp.errorhandler(400)", usr=session["user"], error="Invalid CSRF token."))
            if "delete" in request.form:
                user_collection.delete_one({"Username": usrDelete})
                post_collection.delete_many({"Author": usrDelete})
                flash(f"User {usrDelete} has been deleted.", "success")
                return redirect(url_for("admin.database", usr=session["user"]))
            elif "cancel" in request.form:
                return redirect(url_for("admin.database", usr=session["user"]))
        return render_template("deleteEntry.html", usr=session["user"], usrDelete=usrDelete, form=form)
@admin_bp.route("/database/search/<usr>", methods=["POST"])
def searchEntry(usr):
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            validate_csrf(form.csrf_token.data, app.secret_key)
        except ValidationError:
            return redirect(url_for("error_bp.errorhandler(400)", usr=session["user"], error="Invalid CSRF token."))
        if cl_func.searchValid(form.search.data) == False:
            return redirect(url_for("admin.database", usr=session["user"], error="Invalid search."))
        else:
            userList = admin_func.searchUsers(form.search.data)
            return render_template("database.html", usr=session["user"], userList=userList, form=form)
@admin_bp.route("/database/<usr>/details/<currentUsr>")
def usrDetails(usr, currentUsr):
    if currentUsr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        user = user_collection.find_one({"Username": usr})
        posts_count = post_collection.count_documents({"Author": usr})
        return render_template("details.html", user=user, currentUsr=currentUsr, posts_count=posts_count)