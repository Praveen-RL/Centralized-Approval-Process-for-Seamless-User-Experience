#!/usr/bin/env python3
"""
Script to create admin users in the database
"""
import os
import sys61
from app import app, db
from models import Users, UserRole
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user(username, email, full_name, phone, role, password):
    """Create an admin user if it doesn't exist"""
    with app.app_context():
        # Check if user already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists. Skipping.")
            return existing_user
        
        # Create new user
        user = Users(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        print(f"Created admin user: {email} with role {role.name}")
        return user

def create_all_admin_users():
    """Create all required admin users"""
    # Super Admin
    create_admin_user(
        username="superadmin",
        email="admin@tngovt.gov.in",
        full_name="Super Administrator",
        phone="9876543210",
        role=UserRole.SUPER_ADMIN,
        password="Admin@123"
    )
    
    # Land Admin
    create_admin_user(
        username="landadmin",
        email="land@tngovt.gov.in",
        full_name="Land Department Admin",
        phone="9876543211",
        role=UserRole.LAND_ADMIN,
        password="Land@123"
    )
    
    # Water Admin
    create_admin_user(
        username="wateradmin",
        email="water@tngovt.gov.in",
        full_name="Water Department Admin",
        phone="9876543212",
        role=UserRole.WATER_ADMIN,
        password="Water@123"
    )
    
    # Electricity Admin
    create_admin_user(
        username="electricityadmin",
        email="electricity@tngovt.gov.in",
        full_name="Electricity Department Admin",
        phone="9876543213",
        role=UserRole.ELECTRICITY_ADMIN,
        password="Electricity@123"
    )
    
    # Sewage Admin
    create_admin_user(
        username="sewageadmin",
        email="sewage@tngovt.gov.in",
        full_name="Sewage Department Admin",
        phone="9876543214",
        role=UserRole.SEWAGE_ADMIN,
        password="Sewage@123"
    )

if __name__ == "__main__":
    try:
        create_all_admin_users()
        print("All admin users created successfully.")
    except Exception as e:
        print(f"Error creating admin users: {str(e)}")
        sys.exit(1)