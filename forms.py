from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, TelField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = TelField('Phone Number', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])
    role = SelectField('Account Type', choices=[
        ('USER', 'Service Consumer'),
        ('POWER_USER', 'Service Provider')
    ])
    service_type = SelectField('Service Type', choices=[
        ('', 'Select service type'),
        ('CAR_POOL', 'Car/Bike Pool'),
        ('GYM_FITNESS', 'Gym & Fitness'),
        ('HOUSEHOLD', 'Household'),
        ('MECHANICAL', 'Mechanical')
    ], validators=[Optional()])
    description = TextAreaField('Service Description', validators=[Optional()])