from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class UserRole(enum.Enum):
    CITIZEN = "citizen"
    LAND_ADMIN = "land_admin"
    WATER_ADMIN = "water_admin"
    ELECTRICITY_ADMIN = "electricity_admin"
    SEWAGE_ADMIN = "sewage_admin"
    SUPER_ADMIN = "super_admin"

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.CITIZEN)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True)
    approvals_handled = db.relationship('Approval', backref='admin', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patta_number = db.Column(db.String(50), nullable=False)
    chitta_number = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    district = db.Column(db.String(100))
    taluk = db.Column(db.String(100))
    village = db.Column(db.String(100))
    area_sqft = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    approvals = db.relationship('Approval', backref='property', lazy=True)
    
    def __repr__(self):
        return f'<Property {self.patta_number}>'

class ApprovalType(enum.Enum):
    LAND = "land"
    WATER = "water"
    ELECTRICITY = "electricity"
    SEWAGE = "sewage"

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"

class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    approval_type = db.Column(db.Enum(ApprovalType), nullable=False)
    status = db.Column(db.Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    document_path = db.Column(db.String(255), nullable=False)
    additional_notes = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_notes = db.Column(db.Text)
    approved_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Approval {self.id} - {self.approval_type.value}>'

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<OTP {self.email}>'
