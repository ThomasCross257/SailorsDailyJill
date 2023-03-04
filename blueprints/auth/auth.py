# auth.py

from flask import Blueprint, redirect, render_template, request, session, url_for
import bcrypt
import libs.schemas as schemas
import libs.db_func as db_func
from libs.globals import user_collection, default

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['signin_username']
        password = request.form['signin_password']
        user_data = user_collection.find_one({'Username': user})
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['Password']):
            session['user'] = user
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
        email = request.form['signup_email']
        bio = "This user hasn't updated their bio yet."
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = user_collection.find_one({'Username': user})
        if db_func.is_valid_email(email) == False:
            return redirect(url_for('signup', usr=default, currentUsr=default, error='Not a valid Email address.'))
        if user_data is not None:
            return redirect(url_for('signup', usr=default, currentUsr=default , error='User already exists'))
        is_admin = False
        if user == 'admin':
            is_admin = True
        new_user = schemas.newUser(user, hashed_password, email, is_admin, bio)
        user_collection.insert_one(new_user)
        return redirect(url_for('content.userHome', usr=user, currentUsr=session['user']))
    else:
        return render_template('signup.html', usr=default, currentUsr=default)

@auth_bp.route("/<usr>/logout")
def logout_r(usr):
    if "user" in session:
        session.pop("user", None)
        return render_template("logout.html")