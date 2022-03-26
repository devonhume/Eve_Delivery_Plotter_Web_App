from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

##WTForm


class RegisterForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email Address", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    register = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    login = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class CurrentSystem(FlaskForm):
    system = StringField("Current System", validators=[DataRequired()])
    submit_cs = SubmitField("Enter")


class AddAgent(FlaskForm):
    agent_name = StringField("Agent Name", validators=[DataRequired()])
    system = StringField("Agent's System", validators=[DataRequired()])
    jumps = IntegerField("Jumps to Agent", validators=[DataRequired()])
    submit_agent = SubmitField("Submit Agent")


class ConvertAgent(FlaskForm):
    dest_system = StringField("Destination System", validators=[DataRequired()])
    jumps = IntegerField("Jumps to Destination", validators=[DataRequired()])
    submit_conv = SubmitField("Convert to Mission")


class GetCharacter(FlaskForm):
    name = StringField("Character Name", validators=[DataRequired()])
    system = StringField("Character's Current System", validators=[DataRequired()])
    submit_char = SubmitField("Save Character")


class ChooseCharacter(FlaskForm):
    char = SelectField('Characters')
    submit_choice = SubmitField("Choose Character")

class DataCarrier():

    def __init__(self):
        self.char = None
        self.character = None
        self.flag = None
        self.current_destination = None
        self.agents = None
        self.agents_len = None
        self.missions = None
        self.missions_len = None
        self.char_form = None
        self.choose_char_form = None
        self.current_system_form = None
        self.add_agent_form = None