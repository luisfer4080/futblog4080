from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,ValidationError, SelectField, SelectMultipleField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Create a form class

class NameForm(FlaskForm):
    name = StringField("Whats your name" , validators=[DataRequired()])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Whats your name" , validators=[DataRequired()])
    username = StringField("Whats your username" , validators=[DataRequired()])
    email = StringField("Whats your email" , validators=[DataRequired(),Email()])
    password_hash = PasswordField("Create a password" , validators=[DataRequired(), EqualTo('password_hash_2', message='Passwords must match')])
    password_hash_2 = PasswordField("Reenter a password" , validators=[DataRequired()])
    submit = SubmitField("Submit")

class UpdateUserForm(FlaskForm):
    name = StringField("Whats your name" , validators=[DataRequired()])
    username = StringField("Whats your username" , validators=[DataRequired()])
    email = StringField("Whats your email" , validators=[DataRequired(),Email()])
    password_hash = PasswordField("Whats your password" , validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField("Whats the title" , validators=[DataRequired()])
    slug = StringField("Insert a slug" , validators=[DataRequired()])
    content = CKEditorField("Insert Content" , validators=[DataRequired()])
    image = FileField("Insert picture",validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Whats your email" , validators=[DataRequired(),Email()])
    password = PasswordField("Insert your password" , validators=[DataRequired()])
    submit = SubmitField("Submit")

class TeamForm(FlaskForm):
    name = StringField("Name of the team" , validators=[DataRequired()])
    type = SelectField('Type of team', choices=[('empty', 'Select a type of team'), ('National', 'National'), ('Club', 'Club')])
    text = CKEditorField("Team info" , validators=[DataRequired()])
    palmares = CKEditorField("Team palmares" , validators=[DataRequired()])
    image = FileField("Insert picture",validators=[DataRequired()])
    submit = SubmitField("Submit")

class PlayerForm(FlaskForm):
    name = StringField("Name of the football player" , validators=[DataRequired()])
    text = CKEditorField("Player info" , validators=[DataRequired()])
    palmares = CKEditorField("Insert palmares" , validators=[DataRequired()])
    age = IntegerField("Insert the age of the footballer", validators=[DataRequired()])
    birth = DateField("Insert the birth date of the footballer", validators=[DataRequired()])
    nationality = StringField("Insert the nationality of the footballer" , validators=[DataRequired()])
    position = SelectField('Select the prolific position of the fottballer', choices=[('empty', 'Select a the position of the footballer'), ('GK', 'Goalkeeper'), ('CB', 'Center Back'),('LB', 'Left Back'), ('RB', 'Right Back'), ('CDM', 'Center Defensive Mid'),
                                                    ('CM', 'Center Mid'), ('CAM', 'Center Atacking Mid'), ('LM', 'Left MId'), ('RM', 'Right Mid'), ('LW', 'Left Wing'), ('Rw', 'Right Wing'), ('CF', 'Center Foward'), ('ST', 'Striker')], validators=[DataRequired()])
    team_disp = StringField("Name of the new team")
    image = FileField("Insert big picture",validators=[DataRequired()])
    image_sm = FileField("Insert player profile picture",validators=[DataRequired()])
    team = SelectMultipleField('Select prolific team', coerce=int, validators=[DataRequired()])            

    submit = SubmitField("Submit")


class TestForm(FlaskForm):
    team_disp = StringField("Name of the new team")
    team_choices = [('0', 'New'),('1','Croatia'),('2','Real Madrid')]
    team = SelectMultipleField('Select team (Max 2 choices)', choices = team_choices)    
    submit=SubmitField('Lets Go!')  

