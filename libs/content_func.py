from libs.globals import *
from bson.objectid import ObjectId
import re
from libs.schemas import followList
import bcrypt
from libs.auth_func import is_valid_email

def validUsernameLen(username):
    if len(username) >= 4 and len(username) <= 20:
        return True
    return False

def validPasswordLen(password):
    if len(password) >= 8 and len(password) <= 32:
        return True
    return False

def validBioLen(bio):
    if len(bio) <= 500:
        return True
    return False
def validImage(img):
    if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".jpeg"):
        return True
    return False
def createFollowSchema(user):
    if follow_collection.find_one({"Username": user}) is None:
        new_follow = followList(user, [], [])
        follow_collection.insert_one(new_follow)

def isFollowing(user, follow):
    document = follow_collection.find_one({"Username": user})
    if document and document.get("Following"):
        if follow in document["Following"]:
            return True
    return False

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

def generate_post_id():
    post_id = ObjectId()
    return str(post_id)

def tagsValid(tags):
    if not re.match(r"^[a-zA-Z0-9, ]+$", tags):
        return False
    return True

def searchValid(search):
    if search == "":
        return False
    else:
        return True

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

def validateImage(imageForm):
    if imageForm.files["file"].filename == "":
        return False
    if not imageForm.files["file"].filename.endswith(".png", ".jpg", ".jpeg"):
        return "Error: File must be a valid image file."
    return True

def form_has_changes(form, user):
    # Check if any field is blank
    if any(not field.data for field in form if field.name != 'profilePic'):
        return True
    # Check if any field has changed
    if (
        form.username.data != user["Username"] or
        form.bio.data != user["Biography"]
    ):
        return True
    else:
        return False