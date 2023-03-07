from flask import Flask, redirect, url_for, render_template, session, abort, request,flash
import libs.db_func as db_func
from blueprints.admin.admin import admin_bp
from blueprints.auth.auth import auth_bp
from blueprints.content.content import content_bp
from blueprints.errors.errors import error_bp
from libs.globals import default
from libs.schemas import followList
from libs.db_func import createFollowSchema
app = Flask(__name__)
app.secret_key = db_func.secretCreate()

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(error_bp)

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("content.userHome", usr=user, currentUsr=session["user"]))
    else:
        if request.method == "POST":
            createFollowSchema("admin")
            flash("Follow schema created.")
        return render_template("index.html", usr=default, currentUsr=default)

if __name__ == "__main__":

    app.run(debug=True)