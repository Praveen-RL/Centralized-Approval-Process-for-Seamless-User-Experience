import os
import logging
from app import app
from routes import auth, user, admin, property, approval
from flask import render_template, redirect, url_for
from flask_login import current_user

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Register all blueprint routes
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(property.bp)
app.register_blueprint(approval.bp)

# Define main route directly on the app
@app.route('/')
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
