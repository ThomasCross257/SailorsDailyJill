from libs.globals import user_collection 
import bcrypt
from flask import redirect, session, url_for
from libs.auth_func import is_valid_email, usernameExists

def searchUsers(search):
    search = search.lower()
    users = user_collection.find()
    results = []
    for user in users:
        if search in user["Username"].lower():
            results.append(user)
        elif search in user["Email address"].lower():
            results.append(user)
    return results

def update_user(usrEdit, username, email, password, passwordConf, admin):
    # check for blank fields
    if not username.strip() or not email.strip() or not password.strip() or not passwordConf.strip():
        return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Fields cannot be blank"))
    
    User = user_collection.find_one({"Username": usrEdit})
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    passwordConf = bcrypt.hashpw(passwordConf.encode('utf-8'), bcrypt.gensalt())
    
    if bcrypt.checkpw(password, passwordConf):
        if not is_valid_email(email):
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Not a valid Email address."))
        if usernameExists(username, user_collection):
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="User already exists"))
        if user_collection.find_one({"Email address": email}) is not None:
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Email already in use"))
        elif  user_collection.find_one({"Email address": email}) == User['Email address']:
            pass
        if admin == "True":
            admin = True
        else:
            admin = False
        update = {"$set": {"Username": username, "Password": password, "Email": email, "Admin": admin}}
        user_collection.update_one({"Username": usrEdit}, update)
        user_collection.delete_one({"Username": usrEdit})
        return redirect(url_for("admin.database", usr=session["user"]))
    else:
        return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Passwords do not match"))