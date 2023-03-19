from flask import redirect, url_for, render_template, session
from libs.globals import default, mailServer, mailPort, mailUseSSL, mailUsername, mailPassword
from blueprints.admin.admin import admin_bp
from blueprints.auth.auth import auth_bp
from blueprints.content.content import content_bp
from blueprints.errors.errors import error_bp
from app import app

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(error_bp)

app.config['MAIL_SERVER'] = mailServer
app.config['MAIL_PORT'] = mailPort
app.config['MAIL_USE_SSL'] = mailUseSSL
app.config['EMAILUSERNAME'] = mailUsername
app.config['EMAILPASS'] = mailPassword
app.config['EMAILDEFAULT'] = "noReply"

@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("content.userHome", usr=user, currentUsr=session["user"]))
    else:
        return render_template("index.html", usr=default, currentUsr=default)

@app.template_filter('to_string')
def to_string(value):
    return str(value)

if __name__ == "__main__":

    app.run(debug=True)