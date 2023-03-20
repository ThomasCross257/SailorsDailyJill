# auth.py

from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort
import bcrypt
import libs.forms as forms
from libs.globals import user_collection, default
import libs.auth_func as auth_func
from flask_wtf.csrf import validate_csrf, ValidationError
from app import app
import random

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = forms.LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Validate the CSRF token
            try:
                validate_csrf(form.csrf_token.data, app.secret_key)
            except ValidationError:
                abort(400, 'Invalid CSRF token')
            # Verify the user's login information
            user = form.username.data
            password = form.password.data
            remember = form.remember.data
            user_data = user_collection.find_one({'Username': user})
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['Password']):
                session['user'] = user
                if remember == True:
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
            registerResult = auth_func.registerAccount(user, email, password, passwordConf)
            if "Success" in registerResult:
                session['user'] = user
                return redirect(url_for("content.userHome", usr=session["user"], currentUsr=session["user"]))
            else:
                return redirect(url_for('auth.signup', usr=default, currentUsr=default, error=registerResult))
    return render_template('signup.html', usr=default, currentUsr=default, form=form)


@auth_bp.route("/logout/<usr>")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return redirect(url_for("auth.login", usr=default, currentUsr=default))