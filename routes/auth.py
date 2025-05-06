from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app
from models import User, UserRole, OTP
from forms import RegistrationForm, LoginForm, AdminLoginForm, OTPVerificationForm
from utils import generate_otp, send_otp_via_api, store_otp, verify_otp as verify_user_otp, is_government_email
from datetime import datetime
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role=UserRole.CITIZEN,
            is_verified=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Register')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('user.dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role != UserRole.CITIZEN:
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        
        if not is_government_email(email):
            flash('Only official government email addresses are allowed.', 'danger')
            return render_template('auth/admin_login.html', form=form, title='Admin Login')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not registered. Please contact the system administrator.', 'danger')
            return render_template('auth/admin_login.html', form=form, title='Admin Login')
        
        if user.role == UserRole.CITIZEN:
            flash('You are not authorized to access the admin panel.', 'danger')
            return render_template('auth/admin_login.html', form=form, title='Admin Login')
        
        # Generate and send OTP
        otp = generate_otp()
        
        # For testing purposes, show the OTP in the flash message in development
        if current_app.config['DEBUG']:
            logging.info(f"DEBUG MODE: OTP for {email} is {otp}")
            flash(f'DEBUG MODE: Your OTP is {otp}', 'warning')
            
        if send_otp_via_api(email, otp):
            store_otp(email, otp)
            session['admin_email'] = email
            flash('OTP has been sent to your email. Please verify to continue.', 'info')
            return redirect(url_for('auth.verify_otp'))
        else:
            flash('Failed to send OTP. Please try again later.', 'danger')
    
    return render_template('auth/admin_login.html', form=form, title='Admin Login')

@bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'admin_email' not in session:
        return redirect(url_for('auth.admin_login'))
    
    form = OTPVerificationForm()
    if form.validate_on_submit():
        email = session['admin_email']
        otp_code = form.otp.data
        
        if verify_user_otp(email, otp_code):
            user = User.query.filter_by(email=email).first()
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session.pop('admin_email', None)
            flash('OTP verification successful. Welcome to the admin panel!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
    
    return render_template('auth/verify_otp.html', form=form, title='Verify OTP')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
