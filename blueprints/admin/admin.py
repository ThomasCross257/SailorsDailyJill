from flask import Blueprint, render_template, redirect, url_for, request, session, url_for, flash
import libs.db_func as db_func
import libs.schemas as schemas
from libs.globals import user_collection, post_collection
import bcrypt

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix="/admin")

default = "default"

@admin_bp.route("/database/<usr>")
def database(usr):
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        userList = []
        for user in user_collection.find():
            userList.append(user)
        return render_template("database.html", usr=session["user"], userList=userList)

@admin_bp.route("/database/newEntry/<usr>", methods=["GET", "POST"])
def newEntry(usr):
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password_conf = request.form["passwordConf"]
        adminTxt = request.form["admin"]
        print(username, email, password, password_conf, adminTxt)
        # Call the create_user function
        result = db_func.create_user(username, email, password, password_conf, adminTxt)

        if result.startswith("Error"):
            # If there was an error, redirect to newEntry with an error message
            return redirect(url_for("admin.newEntry", usr=session["user"], error=result))
        else:
            # If successful, redirect to database
            return redirect(url_for("admin.database", usr=session["user"]))
    else:
        return render_template("newEntry.html", usr=session["user"])

@admin_bp.route("/database/editEntry/<usr>/<usrEdit>", methods=["GET", "POST"])
def editEntry(usr, usrEdit):
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            passwordConf = request.form["passwordConf"]
            admin = request.form["admin"]
            return db_func.update_user(usrEdit, username, email, password, passwordConf, admin)
        else:
            User = user_collection.find_one({"Username": usrEdit})
            print(User)
            return render_template("editEntry.html", usr=session["user"], User=User)

@admin_bp.route("/content/profile/database/<usr>")
def database_route(usr):
    return redirect(url_for("admin.database", usr=session["user"]))

@admin_bp.route("/database/deleteEntry/<usr>/<usrDelete>", methods=["POST"])
def deleteEntry(usr, usrDelete, methods=["POST", "GET"]):
    if usr != "admin":
        if "user" in session:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            return redirect(url_for("auth.login", usr=default))
    else:
        if request.method == "POST":
            if "delete" in request.form:
                user_collection.delete_one({"Username": usrDelete})
                post_collection.delete_many({"Author": usrDelete})
                flash(f"User {usrDelete} has been deleted.", "success")
                return redirect(url_for("admin.database", usr=session["user"]))
            elif "cancel" in request.form:
                return redirect(url_for("admin.database", usr=session["user"]))
        return render_template("deleteEntry.html", usr=session["user"], usrDelete=usrDelete)