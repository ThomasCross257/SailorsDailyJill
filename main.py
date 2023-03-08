from flask import redirect, url_for, render_template, session
from libs.globals import default
from app import app, csrf


@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("content.userHome", usr=user, currentUsr=session["user"]))
    else:
        return render_template("index.html", usr=default, currentUsr=default)

if __name__ == "__main__":

    app.run(debug=True)