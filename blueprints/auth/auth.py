# auth.py

from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort
import bcrypt
import libs.auth_func as auth_func
from libs.globals import user_collection, default
from app import csrf

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = auth_func.LoginForm()
    if request.method == 'POST':
        remember = True if request.form.get('remember') else False
        if form.validate_on_submit():
            if not csrf.validate_csrf(form.csrf_token.data):
                abort(400, 'Invalid CSRF token')
            user = form.username.data
            password = form.password.data
            user_data = user_collection.find_one({'Username': user})
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['Password']):
                session['user'] = user
                if remember:
                    session.permanent = True
                return redirect(url_for('content.userHome', usr=user, currentUsr=session["user"]))
        else:
            return redirect(url_for('login', usr=default, currentUsr=default, error='Invalid Login Information.'))
    else:
        return render_template('login.html', usr=default, currentUsr=default, form=form)

@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user = request.form['signup_user']
        password = request.form['signup_password']
        verify_password = request.form['signup_passwordVal']
        email = request.form['signup_email']
        registrationResult = auth_func.registerAccount(user, email, password, verify_password)
        if  "Error" in registrationResult:
            return redirect(url_for('signup', usr=default, currentUsr=default, error=registrationResult))
        else: 
            session['user'] = user
            return redirect(url_for('content.userHome', usr=user, currentUsr=session["user"]))
    else:
        return render_template('signup.html', usr=default, currentUsr=default)

@auth_bp.route("/logout/<usr>")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return redirect(url_for("auth.login", usr=default, currentUsr=default))