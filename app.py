from flask import Flask
from libs.auth_func import secretCreate
from blueprints.admin.admin import admin_bp
from blueprints.auth.auth import auth_bp
from blueprints.content.content import content_bp
from blueprints.errors.errors import error_bp
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = secretCreate()

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(error_bp)
csrf = CSRFProtect(app)