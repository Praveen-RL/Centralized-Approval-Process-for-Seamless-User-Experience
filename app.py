import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_required
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Create the app
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Load configuration
app.config.from_object('config.Config')

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
mail.init_app(app)
csrf.init_app(app)

# Import models and create tables
with app.app_context():
    from models import Users, Property, Approval, OTP
    db.create_all()

# Set up login manager
@login_manager.user_loader
def load_user(user_id):
    from models import Users
    return Users.query.get(int(user_id))

# Import main route for index page
from routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

@app.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """Serve uploaded files securely"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
