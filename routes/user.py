from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Users, Property, Approval, UserRole
from forms import ProfileUpdateForm
import logging

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Redirect admin users to admin dashboard
    if current_user.role != UserRole.CITIZEN:
        return redirect(url_for('admin.dashboard'))
    
    # Get user's properties
    properties = Property.query.filter_by(user_id=current_user.id).all()
    property_count = len(properties)
    
    # Get recent approvals
    recent_approvals = Approval.query.join(Property) \
        .filter(Property.user_id == current_user.id) \
        .order_by(Approval.last_updated.desc()) \
        .limit(5) \
        .all()
    
    # Calculate statistics
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    
    all_approvals = Approval.query.join(Property) \
        .filter(Property.user_id == current_user.id) \
        .all()
    
    for approval in all_approvals:
        if approval.status.value == 'pending' or approval.status.value == 'in_review':
            pending_count += 1
        elif approval.status.value == 'approved':
            approved_count += 1
        elif approval.status.value == 'rejected':
            rejected_count += 1
    
    return render_template('user/dashboard.html', 
                          properties=properties,
                          property_count=property_count,
                          recent_approvals=recent_approvals,
                          pending_count=pending_count,
                          approved_count=approved_count,
                          rejected_count=rejected_count,
                          title='Dashboard')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.phone.data = current_user.phone
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/profile.html', form=form, title='Profile')
