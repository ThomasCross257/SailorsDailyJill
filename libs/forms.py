from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, HiddenField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=50)])
    tags = StringField('Tags', validators=[DataRequired(), Length(min=4, max=50)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=4, max=5000)])

class EditProfileForm(FlaskForm):
    username = StringField('Username')
    bio = TextAreaField('Bio')
    passwordConf = PasswordField('Confirm Password')
    profilePic = FileField('Profile Picture')
    csrf_token = HiddenField()


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=20)])
    bio = TextAreaField('Bio', validators=[Length(min=4, max=5000)])
    email = StringField('Email Address', validators=[Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[Length(min=8, max=80)])
    passwordConf = PasswordField('Confirm Password', validators=[Length(min=8, max=80)])
    profilePic = FileField('Profile Picture')
    admin = RadioField('Admin', choices=[('True', 'True'), ('False', 'False')])
    csrf_token = HiddenField()

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.username.default = user["Username"]
        self.bio.default = user["Biography"]
        self.email.default = user["Email address"]
        self.admin.default = user["Admin"]
        self.process()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    passwordConf = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=80)])

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired(), Length(min=4, max=50)])

class ProfileForm(FlaskForm):
    csrf_token = HiddenField()

class DeleteForm(FlaskForm):
    csrf_token = HiddenField()
    yesButton = SubmitField('Yes')
    noButton = SubmitField('No')

class VerifyForm(FlaskForm):
    csrf_token = HiddenField()
    CodeEntry = StringField('Verification Code', validators=[DataRequired(), Length(min=4, max=50)])
    verifyButton = SubmitField('Verify')