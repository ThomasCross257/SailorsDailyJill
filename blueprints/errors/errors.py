from flask import Blueprint, render_template

error_bp = Blueprint('errors', __name__, template_folder='templates')

@error_bp.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@error_bp.errorhandler(403)
def internal_error(error):
    return render_template('403.html'), 403

# Handler for 404 errors
@error_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Handler for 500 errors
@error_bp.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# Handler for all other errors
@error_bp.errorhandler(Exception)
def server_error(error):
    return render_template('error.html', error=error), 500