from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["signin_user"]
        password = request.form["signin_password"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["signup_user"]
        password = request.form["signup_password"]
        email = request.form["signup_email"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("signup.html")

@app.route("/database")
def database():
    return render_template("database.html")

@app.route("/redirect")
def redirect():
    return render_template("redirect.html")

@app.route("/<usr>/home")
def user(usr):
    return render_template("userpage.html")

if __name__ == "__main__":
    app.run()