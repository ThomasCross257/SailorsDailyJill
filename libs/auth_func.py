import bcrypt
from libs.schemas import newUser
from libs.globals import user_collection
import re
import dns.resolver
import secrets
from wtforms import ValidationError

def usernameExists(username, collection):
    if collection.find_one({"Username": username}) is not None:
        return True
    else:
        return False

def is_valid_email(email):
    # Check if the email address is valid according to the email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    # Extract the domain name from the email address
    domain = email.split('@')[1]

    # Query the DNS server for the MX records of the domain
    try:
        dns.resolver.query(domain, 'MX')
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return False

    return True

def registerAccount(username, email, password, passwordConf):
    if not all([username, email, password, passwordConf]):
        return "Error: Required field(s) missing"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_verify = bcrypt.hashpw(passwordConf.encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(hashed_password, hashed_verify) == False and  password != passwordConf:
        return "Error: Passwords do not match"
    if not is_valid_email(email):
        return "Error: Invalid email address"
    if usernameExists(username, user_collection):
        return "Error: Username already exists"
    if user_collection.find_one({"Email address": email}) is not None:
        return "Error: Email already in use"
    new_user = newUser(username, hashed_password, email, False, "This is a new user.")
    user_collection.insert_one(new_user)
    return "Success: User created"

def secretCreate(): # Creates a random secret key for each session
    session_secret = secrets.token_hex(16)
    return session_secret

def password_complexity(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not any(c.isupper() for c in password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not any(c.islower() for c in password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must contain at least one digit')
    if not any(c in "!@#$%^&*()_+-=[]{};:,./<>?" for c in password):
        raise ValidationError('Password must contain at least one special character')