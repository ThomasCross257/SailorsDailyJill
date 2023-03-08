# auth.py

from flask import Blueprint, redirect, render_template, request, session, url_for
import bcrypt
import libs.schemas as schemas
import libs.auth_func as auth_func
from libs.globals import user_collection, default

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['signin_username']
        password = request.form['signin_password']
        remember = True if request.form.get('remember') else False
        user_data = user_collection.find_one({'Username': user})
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['Password']):
            session['user'] = user
            if remember:
                session.permanent = True
            return redirect(url_for('content.userHome', usr=user, currentUsr=session["user"]))
        else:
            return redirect(url_for('login', usr=default, currentUsr=default, error='Invalid Login Information.'))
    else:
        return render_template('login.html', usr=default, currentUsr=default)

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