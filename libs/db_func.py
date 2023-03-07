import re
import dns.resolver
from bson import ObjectId
import secrets
import bcrypt
from flask import redirect, session, url_for
import bcrypt
import libs.db_func as db_func
import libs.schemas as schemas
from libs.globals import user_collection, post_collection, follow_collection

def is_valid_email(email):
    # Check if the email address is valid according to the email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    # Extract the domain name from the email address
    domain = email.split('@')[1]

    # Query the DNS server for the MX records of the domain
    try:
        dns.resolver.query(domain, 'MX')
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return False

    return True
def tagsValid(tags):
    if not re.match(r"^[a-zA-Z0-9, ]+$", tags):
        return False
    return True

def tag_search(tagstring):
    tags = tagstring.split(',')
    return [tag.strip() for tag in tags]

def generate_post_id():
    post_id = ObjectId()
    return str(post_id)

def secretCreate():
    session_secret = secrets.token_hex(16)
    return session_secret

def profileUpdate(newUsername, newEmail, newPassword, verifyPassword, usr, newBio, collection):
    error = None
    hashed_pass = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())
    if newBio == "&nbsp;":
        error= "Bio cannot be empty."
        return error
    if newPassword != "&nbsp;" and verifyPassword != "&nbsp;":
        if newPassword != verifyPassword:
            error= "Passwords do not match."
            return error
        if hashed_pass == collection.find_one({"Username": usr})["Password"]:
            error= "New password cannot be the same as old password."
            return error
    if newEmail != "&nbsp;" and newEmail != collection.find_one({"Username": usr})["Email address"]:
        if is_valid_email(newEmail) == False:
            error = "Invalid Email."
            return error
    if newUsername == usr or newUsername != "&nbsp;":
        if collection.find_one({"Username": newUsername}) is not None:
            error= "Username already Taken"
            return error
        if usr == "admin":
            error = "Cannot change admin username."
            return error
        else:
            collection.update_one({"Username": usr}, {"$set": {"Password": hashed_pass}})
            collection.update_one({"Username": usr}, {"$set": {"Email address": newEmail}})
            collection.update_one({"Username": usr}, {"$set": {"Username": newUsername}})
            return "Success!"

def usernameExists(username, collection):
    if collection.find_one({"Username": username}) is not None:
        return True
    else:
        return False
def signedInUser(user, session):
    if session["user"] == user:
        return True
    else:
        return False
def create_user(username, email, password, password_conf, admin):
    # Check if any required fields are blank
    if not all([username, email, password, password_conf, admin]):
        return "Error: Required field(s) missing"
    if admin == "True":
        admin = True
    else:
        admin = False
    # Hash the passwords
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_conf = bcrypt.hashpw(password_conf.encode('utf-8'), bcrypt.gensalt())

    # Check if the passwords match
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password_conf) == False:
        return "Error: Passwords do not match"

    # Check if the email is valid
    if not db_func.is_valid_email(email):
        return "Error: Invalid email address"

    # Check if the username or email already exists
    if user_collection.find_one({"Username": username}) is not None:
        return "Error: Username already exists"
    if user_collection.find_one({"Email": email}) is not None:
        return "Error: Email already in use"

    # Convert admin field to boolean
    if admin == "True":
        admin = True
    else:
        admin = False

    # Generate a new user object using the schema
    new_user = schemas.newUser(username, hashed_password, email, admin, "This is a new user.")

    # Insert the new user into the database
    user_collection.insert_one(new_user)

    return "Success: User created"



def update_user(usrEdit, username, email, password, passwordConf, admin):
    # check for blank fields
    if not username.strip() or not email.strip() or not password.strip() or not passwordConf.strip():
        return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Fields cannot be blank"))
    
    User = user_collection.find_one({"Username": usrEdit})
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    passwordConf = bcrypt.hashpw(passwordConf.encode('utf-8'), bcrypt.gensalt())
    
    if bcrypt.checkpw(password, passwordConf):
        if not db_func.is_valid_email(email):
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

def searchPosts(search):
    search = search.lower()
    posts = post_collection.find()
    results = []
    for post in posts:
        if search in post["Title"].lower():
            results.append(post)
        elif search in post["Tags"].lower():
            results.append(post)
        elif search in post["Author"].lower():
            results.append(post)
    return results
def searchValid(search):
    if search == "":
        return False
    else:
        return True
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

def registerAccount(username, email, password, passwordConf):
    if not all([username, email, password, passwordConf]):
        return "Error: Required field(s) missing"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_verify = bcrypt.hashpw(passwordConf.encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(hashed_password, hashed_verify) == False:
        return "Error: Passwords do not match"
    if not is_valid_email(email):
        return "Error: Invalid email address"
    if usernameExists(username, user_collection):
        return "Error: Username already exists"
    if user_collection.find_one({"Email address": email}) is not None:
        return "Error: Email already in use"
    new_user = schemas.newUser(username, hashed_password, email, False, "This is a new user.")
    user_collection.insert_one(new_user)
    return "Success: User created"
def followUser(follow, user):
    if user == follow:
        return "Error: Cannot follow yourself"
    if user_collection.find_one({"Username": follow}) is None:
        return "Error: User does not exist"
    createFollowSchema(user)
    createFollowSchema(follow)
    if follow_collection.find_one({"Username": user})["Following"] is not None:
        if follow in follow_collection.find_one({"Username": user})["Following"]:
            follow_collection.update_one({"Username": follow}, {"$pull": {"Followers": user}})
            follow_collection.update_one({"Username": user}, {"$pull": {"Following": follow}})
            return "Success: User unfollowed"
        else:
            follow_collection.update_one({"Username": follow}, {"$push": {"Followers": user}})
            follow_collection.update_one({"Username": user}, {"$push": {"Following": follow}})
            return "Success: User followed"

def isFollowing(user, follow):
    if follow_collection.find_one({"Username": user})["Following"] is not None:
        if follow in follow_collection.find_one({"Username": user})["Following"]:
            return True
    return False
def createFollowSchema(user):
    if follow_collection.find_one({"Username": user}) is None:
        new_follow = schemas.followList(user, [], [])
        follow_collection.insert_one(new_follow)