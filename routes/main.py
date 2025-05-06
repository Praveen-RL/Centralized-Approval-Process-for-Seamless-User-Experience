from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page route"""
    if current_user.is_authenticated:
        # If user is logged in, redirect to appropriate dashboard
        if current_user.role.name == 'CITIZEN':
            return redirect(url_for('user.dashboard'))
        else:
            return redirect(url_for('admin.dashboard'))
    # If not logged in, show home page
    return render_template('index.html', title='Home')
