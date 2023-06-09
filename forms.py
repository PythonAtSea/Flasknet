from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1,64)])
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Passsword", validators=[Length(8,100), DataRequired()])
    passwordconfirm = PasswordField("Passsword", validators=[EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("That username is taken.")
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("That email is taken.")

class EditForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1,64)])
    about = TextAreaField("About Me", validators=[Length(0,200)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.original_username=original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("That username is in use.")

class EmptyForm(FlaskForm):
    submit=SubmitField("Submit")

class PostForm(FlaskForm):
    post = TextAreaField("Say Something", validators=[DataRequired(), Length(1,500)])
    submit = SubmitField("Post")
