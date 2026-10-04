from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from models import Property, Approval, ApprovalType, ApprovalStatus, UserRole
from forms import ApprovalForm
from utils import save_document, validate_pdf, send_notification_email, get_approval_department
import logging
import os

bp = Blueprint('approval', __name__, url_prefix='/approval')

@bp.route('/apply/<int:property_id>', methods=['GET', 'POST'])
@login_required
def apply(property_id):
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can submit approval applications.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    property = Property.query.get_or_404(property_id)
    
    # Check if property belongs to current user
    if property.user_id != current_user.id:
        abort(403)
    
    form = ApprovalForm()
    if form.validate_on_submit():
        approval_type = ApprovalType(form.approval_type.data)
        
        # Check if approval application for this type already exists
        existing_approval = Approval.query.filter_by(
            property_id=property_id,
            approval_type=approval_type
        ).first()
        
        if existing_approval:
            flash(f'An application for {approval_type.value.capitalize()} Approval already exists for this property.', 'warning')
            return redirect(url_for('property.detail', property_id=property_id))
        
        # Validate PDF
        if not validate_pdf(form.document.data):
            flash('Invalid PDF document. Please upload a valid PDF file.', 'danger')
            return render_template('user/approval_form.html', form=form, property=property, title='Apply for Approval')
        
        # Save document
        document_path = save_document(form.document.data)
        if not document_path:
            flash('Failed to save document. Please try again.', 'danger')
            return render_template('user/approval_form.html', form=form, property=property, title='Apply for Approval')
        
        # Create approval application
        approval = Approval(
            property_id=property_id,
            approval_type=approval_type,
            status=ApprovalStatus.PENDING,
            document_path=document_path,
            additional_notes=form.additional_notes.data
        )
        
        db.session.add(approval)
        db.session.commit()
        
        department = get_approval_department(approval_type)
        
        flash(f'Approval application submitted successfully! Your application has been sent to the {department}.', 'success')
        return redirect(url_for('property.detail', property_id=property_id))
    
    return render_template('user/approval_form.html', form=form, property=property, title='Apply for Approval')

@bp.route('/status/<int:approval_id>')
@login_required
def status(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    property = Property.query.get(approval.property_id)
    
    # Check if user has permission to view this approval
    if current_user.role == UserRole.CITIZEN:
        if property.user_id != current_user.id:
            abort(403)
    elif current_user.role != UserRole.SUPER_ADMIN:
        expected_role = approval.approval_type.value + '_admin'
        if current_user.role.value != expected_role:
            abort(403)
    
    # Generate document URL using url_for
    document_path = url_for('serve_upload', filename=os.path.basename(approval.document_path)) if approval.document_path else None
    
    return render_template('user/approval_status.html', 
                          approval=approval, 
                          property=property,
                          document_path=document_path,
                          title='Approval Status')

@bp.route('/cancel/<int:approval_id>', methods=['POST'])
@login_required
def cancel(approval_id):
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can cancel approval applications.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    approval = Approval.query.get_or_404(approval_id)
    property = Property.query.get(approval.property_id)
    
    # Check if property belongs to current user
    if property.user_id != current_user.id:
        abort(403)
    
    # Check if approval can be canceled
    if approval.status != ApprovalStatus.PENDING:
        flash('Only pending applications can be canceled.', 'danger')
        return redirect(url_for('approval.status', approval_id=approval_id))
    
    # Delete document file if it exists
    if approval.document_path and os.path.exists(approval.document_path):
        try:
            os.remove(approval.document_path)
        except Exception as e:
            logging.error(f"Failed to delete document: {str(e)}")
    
    db.session.delete(approval)
    db.session.commit()
    
    flash('Approval application canceled successfully!', 'success')
    return redirect(url_for('property.detail', property_id=property.id))
