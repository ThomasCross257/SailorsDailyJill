from flask import Flask
from flask_wtf.csrf import CSRFProtect
from libs.auth_func import secretCreate

app = Flask(__name__)


csrf = CSRFProtect(app)
app.secret_key = secretCreate()
