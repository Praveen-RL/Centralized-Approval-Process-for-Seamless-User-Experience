from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import Users, Property, Approval, UserRole, ApprovalStatus, ApprovalType
from forms import AdminApprovalForm
from utils import get_approval_department, get_role_for_approval_type, send_notification_email
from datetime import datetime
import logging
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Ensure user is an admin
    if current_user.role == UserRole.CITIZEN:
        flash('You do not have permission to access the admin panel.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # Get approvals based on admin role
    approvals_query = Approval.query
    
    if current_user.role != UserRole.SUPER_ADMIN:
        approval_type = None
        if current_user.role == UserRole.LAND_ADMIN:
            approval_type = ApprovalType.LAND
        elif current_user.role == UserRole.WATER_ADMIN:
            approval_type = ApprovalType.WATER
        elif current_user.role == UserRole.ELECTRICITY_ADMIN:
            approval_type = ApprovalType.ELECTRICITY
        elif current_user.role == UserRole.SEWAGE_ADMIN:
            approval_type = ApprovalType.SEWAGE
        
        if approval_type:
            approvals_query = approvals_query.filter_by(approval_type=approval_type)
    
    # Get statistics
    pending_count = approvals_query.filter_by(status=ApprovalStatus.PENDING).count()
    in_review_count = approvals_query.filter_by(status=ApprovalStatus.IN_REVIEW).count()
    approved_count = approvals_query.filter_by(status=ApprovalStatus.APPROVED).count()
    rejected_count = approvals_query.filter_by(status=ApprovalStatus.REJECTED).count()
    info_needed_count = approvals_query.filter_by(status=ApprovalStatus.ADDITIONAL_INFO_NEEDED).count()
    
    # Get recent approvals
    recent_approvals = approvals_query.order_by(Approval.last_updated.desc()).limit(10).all()
    
    department = get_approval_department(ApprovalType(current_user.role.name.split('_')[0].lower())) if current_user.role != UserRole.SUPER_ADMIN else "All Departments"
    
    return render_template('admin/dashboard.html',
                          recent_approvals=recent_approvals,
                          pending_count=pending_count,
                          in_review_count=in_review_count,
                          approved_count=approved_count,
                          rejected_count=rejected_count,
                          info_needed_count=info_needed_count,
                          department=department,
                          title='Admin Dashboard')

@bp.route('/approvals')
@login_required
def approval_requests():
    # Ensure user is an admin
    if current_user.role == UserRole.CITIZEN:
        flash('You do not have permission to access the admin panel.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Build query based on admin role and filters
    approvals_query = Approval.query
    
    # Filter by admin role
    if current_user.role != UserRole.SUPER_ADMIN:
        approval_type = None
        if current_user.role == UserRole.LAND_ADMIN:
            approval_type = ApprovalType.LAND
        elif current_user.role == UserRole.WATER_ADMIN:
            approval_type = ApprovalType.WATER
        elif current_user.role == UserRole.ELECTRICITY_ADMIN:
            approval_type = ApprovalType.ELECTRICITY
        elif current_user.role == UserRole.SEWAGE_ADMIN:
            approval_type = ApprovalType.SEWAGE
        
        if approval_type:
            approvals_query = approvals_query.filter_by(approval_type=approval_type)
    
    # Filter by status
    if status_filter != 'all':
        try:
            status = ApprovalStatus(status_filter)
            approvals_query = approvals_query.filter_by(status=status)
        except ValueError:
            pass
    
    # Get all approvals with property and owner information
    approvals = approvals_query.join(Property).join(Users, Property.user_id == Users.id) \
        .order_by(Approval.application_date.desc()) \
        .all()
    
    return render_template('admin/approval_requests.html',
                          approvals=approvals,
                          status_filter=status_filter,
                          title='Approval Requests')

@bp.route('/approval/<int:approval_id>', methods=['GET', 'POST'])
@login_required
def approval_detail(approval_id):
    # Ensure user is an admin
    if current_user.role == UserRole.CITIZEN:
        flash('You do not have permission to access the admin panel.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    approval = Approval.query.get_or_404(approval_id)
    property = Property.query.get(approval.property_id)
    owner = Users.query.get(property.user_id)
    
    # Check if admin has authority over this approval type
    if current_user.role != UserRole.SUPER_ADMIN:
        expected_role = get_role_for_approval_type(approval.approval_type)
        if current_user.role != expected_role:
            flash('You do not have permission to process this type of approval.', 'danger')
            return redirect(url_for('admin.approval_requests'))
    
    form = AdminApprovalForm()
    
    if form.validate_on_submit():
        approval.status = ApprovalStatus(form.status.data)
        approval.admin_id = current_user.id
        approval.admin_notes = form.admin_notes.data
        
        if approval.status == ApprovalStatus.APPROVED:
            approval.approved_date = datetime.utcnow()
        
        db.session.commit()
        
        # Send notification email
        subject = f"Update on your {approval.approval_type.value.capitalize()} Approval Application"
        body = f"""Dear {owner.full_name},

Your {approval.approval_type.value.capitalize()} Approval application for property at {property.address} has been updated.

Status: {approval.status.value.replace('_', ' ').capitalize()}

Admin Notes: {approval.admin_notes}

Please log in to your account to view the details.

Thank you,
Tamil Nadu Government House Construction Approval System
"""
        send_notification_email(owner.email, subject, body)
        
        flash('Approval status updated successfully!', 'success')
        return redirect(url_for('admin.approval_requests'))
    
    # For GET request, populate the form with current data
    if request.method == 'GET' and approval.admin_notes:
        form.admin_notes.data = approval.admin_notes
    
    # Generate document URL using url_for
    document_path = url_for('serve_upload', filename=os.path.basename(approval.document_path)) if approval.document_path else None
    
    return render_template('admin/approval_detail.html',
                          approval=approval,
                          property=property,
                          owner=owner,
                          form=form,
                          document_path=document_path,
                          title='Approval Details')
