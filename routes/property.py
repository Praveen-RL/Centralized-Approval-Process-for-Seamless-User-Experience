from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import Property, Approval, UserRole
from forms import PropertyRegistrationForm
import logging

bp = Blueprint('property', __name__, url_prefix='/property')

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can register properties.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    form = PropertyRegistrationForm()
    if form.validate_on_submit():
        property = Property(
            user_id=current_user.id,
            patta_number=form.patta_number.data,
            chitta_number=form.chitta_number.data,
            address=form.address.data,
            district=form.district.data,
            taluk=form.taluk.data,
            village=form.village.data,
            area_sqft=form.area_sqft.data
        )
        
        db.session.add(property)
        db.session.commit()
        
        flash('Property registered successfully!', 'success')
        return redirect(url_for('property.list'))
    
    return render_template('user/property_register.html', form=form, title='Register Property')

@bp.route('/list')
@login_required
def list():
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can view their properties.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    properties = Property.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/property_list.html', properties=properties, title='My Properties')

@bp.route('/<int:property_id>')
@login_required
def detail(property_id):
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can view property details.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    property = Property.query.get_or_404(property_id)
    
    # Check if property belongs to current user
    if property.user_id != current_user.id:
        abort(403)
    
    # Get all approvals for this property
    approvals = Approval.query.filter_by(property_id=property_id).all()
    
    return render_template('user/property_detail.html', 
                          property=property, 
                          approvals=approvals,
                          title='Property Details')

@bp.route('/delete/<int:property_id>', methods=['POST'])
@login_required
def delete(property_id):
    # Ensure user is a citizen
    if current_user.role != UserRole.CITIZEN:
        flash('Only citizens can delete properties.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    property = Property.query.get_or_404(property_id)
    
    # Check if property belongs to current user
    if property.user_id != current_user.id:
        abort(403)
    
    # Check if property has any approvals
    approvals = Approval.query.filter_by(property_id=property_id).all()
    if approvals:
        flash('Cannot delete property with existing approval applications.', 'danger')
        return redirect(url_for('property.detail', property_id=property_id))
    
    db.session.delete(property)
    db.session.commit()
    
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('property.list'))
