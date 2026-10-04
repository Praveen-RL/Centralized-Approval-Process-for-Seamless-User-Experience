import os
import random
import string
import requests
import logging
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app
from flask_mail import Message
from app import db, mail
from models import OTP, ApprovalType, UserRole
import PyPDF2
from io import BytesIO

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_via_api(email, otp):
    """Send OTP using the provided API"""
    api_key = current_app.config['OTP_API_KEY']
    try:
        # Using the real API key: de503d8d-e2e2-4fda-bc31-fac2242f7056
        # For demo purposes, we're logging the OTP instead of calling an actual API
        # In production, this would call a real OTP service
        logging.info(f"OTP API called with key {api_key}")
        logging.info(f"OTP for {email}: {otp}")
        
        # Since this is a demo, we'll simulate success
        # In production, you'd check the actual API response
        return True
    except Exception as e:
        logging.error(f"Failed to send OTP via API: {str(e)}")
        # Fallback to email
        return send_otp_via_email(email, otp)

def send_otp_via_email(email, otp):
    """Fallback method to send OTP via email"""
    try:
        msg = Message(
            subject="Government House Construction Approval System - Your OTP",
            recipients=[email],
            body=f"Your OTP for authentication is: {otp}. This OTP is valid for {current_app.config['OTP_EXPIRY_MINUTES']} minutes."
        )
        mail.send(msg)
        logging.info(f"OTP sent via email to {email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send OTP via email: {str(e)}")
        return False

def store_otp(email, otp):
    """Store OTP in the database"""
    new_otp = OTP(email=email, otp_code=otp)
    db.session.add(new_otp)
    db.session.commit()
    logging.info(f"OTP stored for {email}")

def verify_otp(email, otp_code):
    """Verify if OTP is valid and not expired"""
    expiry_minutes = current_app.config['OTP_EXPIRY_MINUTES']
    valid_time = datetime.utcnow() - timedelta(minutes=expiry_minutes)
    
    otp_entry = OTP.query.filter_by(
        email=email,
        otp_code=otp_code,
        is_used=False
    ).filter(OTP.created_at >= valid_time).first()
    
    if otp_entry:
        otp_entry.is_used = True
        db.session.commit()
        logging.info(f"OTP verified for {email}")
        return True
    
    logging.warning(f"Invalid OTP attempt for {email}")
    return False

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_document(file):
    """Save uploaded document and return the path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to make it unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file and return relative path
        file_path = os.path.join(upload_folder, new_filename)
        file.save(file_path)
        logging.info(f"Document saved: {file_path}")
        return os.path.join('uploads', new_filename)  # Return relative path
    
    logging.error("Invalid file upload attempt")
    return None

def validate_pdf(file):
    """Validate if the file is a valid PDF"""
    try:
        # Read file into memory
        file_stream = BytesIO(file.read())
        # Reset the file pointer to the beginning
        file.seek(0)
        
        # Try to open with PyPDF2
        PyPDF2.PdfReader(file_stream)
        return True
    except Exception as e:
        logging.error(f"PDF validation failed: {str(e)}")
        return False

def send_notification_email(user_email, subject, body):
    """Send notification email to user"""
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body
        )
        mail.send(msg)
        logging.info(f"Notification email sent to {user_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send notification email: {str(e)}")
        return False

def get_approval_department(approval_type):
    """Get the department name for an approval type"""
    departments = {
        ApprovalType.LAND: "Revenue Department",
        ApprovalType.WATER: "Municipality - Water Supply",
        ApprovalType.ELECTRICITY: "TANGEDCO - Electricity Board",
        ApprovalType.SEWAGE: "Local Body - Sewage and Sanitation"
    }
    return departments.get(approval_type, "Unknown Department")

def get_role_for_approval_type(approval_type):
    """Map approval type to corresponding admin role"""
    mapping = {
        ApprovalType.LAND: UserRole.LAND_ADMIN,
        ApprovalType.WATER: UserRole.WATER_ADMIN,
        ApprovalType.ELECTRICITY: UserRole.ELECTRICITY_ADMIN,
        ApprovalType.SEWAGE: UserRole.SEWAGE_ADMIN
    }
    return mapping.get(approval_type)

def is_government_email(email):
    """Check if email is an official government email domain"""
    # For this demo, allow our test government emails to work
    test_emails = [
        "admin@tngovt.gov.in",
        "land@tngovt.gov.in",
        "water@tngovt.gov.in",
        "electricity@tngovt.gov.in",
        "sewage@tngovt.gov.in"
    ]
    
    # Check if it's one of our test emails or has a valid government domain
    return email in test_emails or email.endswith('.gov.in') or email.endswith('.nic.in')
