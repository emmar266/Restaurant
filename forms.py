from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField, validators
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange, Email
from wtforms.widgets import TextArea


class RegistrationForm(FlaskForm):
    email = StringField("Email Address", [InputRequired(), validators.Length(min=6, max=100), Email(message="Please enter a valid Email Address!")])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")
