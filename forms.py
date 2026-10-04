from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from models import Users

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Phone number must be 10 digits')
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login & Send OTP')

class AdminLoginForm(FlaskForm):
    email = StringField('Official Email', validators=[
        DataRequired(), 
        Email(), 
        Regexp(r'.*@.*\.gov\.in$', message='Must be an official government email')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login & Send OTP')

class OTPVerificationForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[
        DataRequired(),
        Regexp(r'^\d{6}$', message='OTP must be 6 digits')
    ])
    submit = SubmitField('Verify')

class PropertyRegistrationForm(FlaskForm):
    patta_number = StringField('Patta Number', validators=[DataRequired()])
    chitta_number = StringField('Chitta Number', validators=[DataRequired()])
    address = TextAreaField('Property Address', validators=[DataRequired()])
    district = StringField('District', validators=[DataRequired()])
    taluk = StringField('Taluk', validators=[DataRequired()])
    village = StringField('Village', validators=[DataRequired()])
    area_sqft = FloatField('Area (in sq. ft.)', validators=[DataRequired()])
    submit = SubmitField('Register Property')

class ApprovalForm(FlaskForm):
    approval_type = SelectField('Approval Type', choices=[
        ('land', 'Land Approval'),
        ('water', 'Water Supply Approval'),
        ('electricity', 'Electricity Connection Approval'),
        ('sewage', 'Sewage and Sanitation Approval')
    ], validators=[DataRequired()])
    document = FileField('Upload Document (PDF only)', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF documents only!')
    ])
    additional_notes = TextAreaField('Additional Notes')
    submit = SubmitField('Submit Application')

class AdminApprovalForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('in_review', 'Mark as In Review'),
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
        ('additional_info_needed', 'Request Additional Information')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit Decision')

class ProfileUpdateForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField('Phone Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Phone number must be 10 digits')
    ])
    submit = SubmitField('Update Profile')
