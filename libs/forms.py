from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, FileAllowed

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=50)])
    tags = StringField('Tags', validators=[DataRequired(), Length(min=4, max=50)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=4, max=5000)])

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    bio = TextAreaField('Bio', validators=[DataRequired(), Length(min=4, max=5000)])
    email = StringField('Email Address', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    passwordConf = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=80)])
    profilePic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    passwordConf = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=80)])
