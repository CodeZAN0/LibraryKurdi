from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField, SubmitField, PasswordField  # Add PasswordField here
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileAllowed  # Import FileAllowed from flask_wtf.file
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TelField
from wtforms.validators import DataRequired, EqualTo, Email

class LoginForm(FlaskForm):
    identifier = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Upload Avatar', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    phone = TelField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Register')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    writer = StringField('Writer', validators=[DataRequired()])
    cover = FileField('Cover Image', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    file = FileField('PDF File', validators=[DataRequired(), FileAllowed(['pdf'], 'PDFs only!')])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])  # SelectField for categories
    submit = SubmitField('Add Book')
