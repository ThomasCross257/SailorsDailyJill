from libs.globals import user_collection 
import bcrypt
from flask import redirect, session, url_for
from libs.auth_func import is_valid_email, usernameExists

def searchUsers(search):
    # convert search string to lowercase
    search = search.lower()
    # get all users from user_collection
    users = user_collection.find()
    # initialize empty list to store search results
    results = []
    # loop through each user
    for user in users:
        # check if search string is a substring of username in lowercase
        if search in user["Username"].lower():
            # if so, add the user to results list
            results.append(user)
        # check if search string is a substring of email address in lowercase
        elif search in user["Email address"].lower():
            # if so, add the user to results list
            results.append(user)
    # return the list of matching users
    return results



# Updating user profile via admin database.
def update_user(usrEdit, username, email, password, passwordConf, admin):
    # check for blank fields
    if not username.strip() or not email.strip() or not password.strip() or not passwordConf.strip():
        return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Fields cannot be blank"))
    
    # Get the user data from the database using the username
    User = user_collection.find_one({"Username": usrEdit})

    # Hash the password and password confirmation for security
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    passwordConf = bcrypt.hashpw(passwordConf.encode('utf-8'), bcrypt.gensalt())

    # Check if the password and password confirmation match
    if bcrypt.checkpw(password, passwordConf):
        # Check if the email is a valid email format
        if not is_valid_email(email):
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Not a valid Email address."))
        # Check if the new username already exists in the database
        if usernameExists(username, user_collection):
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="User already exists"))
        # Check if the new email already exists in the database
        if user_collection.find_one({"Email address": email}) is not None:
            return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Email already in use"))
        # If the email is not updated, skip the check
        elif user_collection.find_one({"Email address": email}) == User['Email address']:
            pass
        
        # Convert the admin radio input to a boolean value
        if admin == "True":
            admin = True
        else:
            admin = False

        # Update the user data in the database
        update = {"$set": {"Username": username, "Password": password, "Email": email, "Admin": admin}}
        user_collection.update_one({"Username": usrEdit}, update)

        # Delete the old user data from the database
        user_collection.delete_one({"Username": usrEdit})

        # Redirect to the admin database page
        return redirect(url_for("admin.database", usr=session["user"]))

    # If the password and password confirmation do not match, redirect back to the edit page with an error message
    else:
        return redirect(url_for("admin.editEntry", usr=session["user"], usrEdit=usrEdit, error="Passwords do not match"))
