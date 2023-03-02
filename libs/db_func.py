import re
import dns.resolver
from bson import ObjectId
import secrets
import bcrypt

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

def profileUpdate_Check(usrCheck,emailCheck,passCheck):
    
    return False
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