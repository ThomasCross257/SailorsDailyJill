def newUser(user, password, email, adminPermission, biography):
    new_user ={
        "Username" : user,
        "Password" : password,
        "Email address" : email,
        "Admin" : adminPermission,
        "Biography" : biography,
        "Profile URL": "/static/img/default.jpg",
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
def newComment(comment, author, date, post_id):
    new_comment = {
        '_id' : post_id,
        "Comment" : comment,
        "Author" : author,
        "Date" : date
    }
    return new_comment
def newReply(reply, author, date, comment_id):
    new_reply = {
        '_id' : comment_id,
        "Reply" : reply,
        "Author" : author,
        "Date" : date
    }
    return new_reply
def followList(username, following, follower):
    new_follow = {
        "Username" : username,
        "Following" : following,
        "Followers" : follower
    }
    return new_follow