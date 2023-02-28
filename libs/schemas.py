def newUser(user, password, email, adminPermission):
    new_user ={
        "Username" : user,
        "Password" : password,
        "Email address" : email,
        "Admin" : adminPermission
    }
    return new_user
def newPost(title, content, author, date, tags, post_id):
    new_post = {
        '_id' : post_id,
        "Title" : title,
        "Content" : content,
        "Author" : author,
        "Date" : date,
        "Tags" : tags
    }
    return new_post