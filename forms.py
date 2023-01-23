from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange
"""
class RegisterForm(FlaskForm):
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    surname = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")
"""
class OngoingForm(FlaskForm):
    index=IntegerField('Order Number: ')
    submit=SubmitField('Set to ongoing')

class DeleteForm(FlaskForm):
    index=IntegerField('Order Number: ')
    submit=SubmitField('Delete meal')