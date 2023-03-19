# auth.py

from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort
import bcrypt
import libs.forms as forms
from libs.globals import user_collection, default, mailUsername
import libs.auth_func as auth_func
from flask_wtf.csrf import validate_csrf, ValidationError
from app import app
from flask_mail import Mail, Message
import random

mail = Mail(app)

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = forms.LoginForm()
    if request.method == 'POST':
        if request.form.get('remember'):
            remember = True 
        else:
            remember = False
        if form.validate_on_submit():
            # Validate the CSRF token
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                abort(400, 'Invalid CSRF token')
            # Verify the user's login information
            user = form.username.data
            password = form.password.data
            user_data = user_collection.find_one({'Username': user})
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['Password']):
                session['user'] = user
                if remember:
                    session.permanent = True
                return redirect(url_for('content.userHome', usr=user, currentUsr=session["user"]))
            else:
                return redirect(url_for('auth.login', usr=default, currentUsr=default, error='Invalid Login Information.'))
        else:
            return redirect(url_for('auth.login', usr=default, currentUsr=default, error='Invalid Login Information.'))
    else:
        return render_template('login.html', usr=default, currentUsr=default, form=form)
    
@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    form = forms.RegisterForm()
    if request.method == 'POST':
        print(form.validate_on_submit())
        if form.validate_on_submit():
            # Validate the CSRF token
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                abort(400, 'Invalid CSRF token')
            # Verify the user's login information
            user = form.username.data
            password = form.password.data
            email = form.email.data
            passwordConf = form.passwordConf.data
            verificationcode = str(random.randint(100000, 999999))
            registerResult = auth_func.registerAccount(user, email, password, passwordConf, verificationcode)
            if "Success" in registerResult:
                session["user"] = user
                msg = Message("Verify your account", sender=("noReply", mailUsername), recipients=[email])
                msg.body = "Hello, " + user + "! Your verification code is " + verificationcode + ". It will expire within five minutes."
                mail.send(msg)
                return redirect(url_for('auth.verify', usr=user, currentUsr=session["user"]))
            else:
                return redirect(url_for('auth.signup', usr=default, currentUsr=default, error=registerResult))
    return render_template('signup.html', usr=default, currentUsr=default, form=form)


@auth_bp.route("/logout/<usr>")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return redirect(url_for("auth.login", usr=default, currentUsr=default))

@auth_bp.route("/verify/<usr>", methods=["POST", "GET"])
def verify(usr):
    if "user" in session:
        verificationCheck = user_collection.find_one({"Username": usr})
        if verificationCheck["Verified"] == True:
            return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
        else:
            form = forms.VerifyForm()
            if request.method == "POST":
                if form.validate_on_submit():
                    # Validate the CSRF token
                    try:
                        validate_csrf(form.csrf_token.data, app.secret_key)
                    except ValidationError:
                        abort(400, 'Invalid CSRF token')
                    # Verify the user's login information
                    code = form.code.data
                    if bcrypt.checkpw(code.encode('utf-8'), verificationCheck["VerificationCode"]):
                        user_collection.update_one({"Username": usr}, {"$set": {"Verified": True}})
                        return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
                    else:
                        flash("Invalid verification code.")
                        return redirect(url_for("auth.verify", usr=usr, currentUsr=session["user"]))
                else:
                    return redirect(url_for("auth.verify", usr=usr, currentUsr=session["user"], error="Invalid verification code."))
            else:
                return render_template("verify.html", usr=session["user"], currentUsr=session["user"], form=form)
    else:
        return redirect(url_for("auth.login", usr=default, currentUsr=default))