from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# class SignupForm(FlaskForm):
#     firstname = StringField('First name', validators=[DataRequired()])
#     lastname = StringField('Last name', validators=[DataRequired()])
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Repeat password', [InputRequired()])
#     emailid = StringField('Email address', validators=[DataRequired()])
