from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired

"""
class RegisterForm(FlaskForm):
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    surname = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")
"""

class AddDish(FlaskForm):
    name = StringField('Dish Name: ', validators=[InputRequired()])
    cost = IntegerField('Dish Price', validators=[InputRequired()])
    cookTime= IntegerField('Cook Time', validators=[InputRequired()])
    dishType = StringField('Dish type:',validators=[InputRequired()])
    dishDescription = TextAreaField('Dish Description: ')
    dishPic = FileField('Upload a picture of dish:',validators=[FileRequired(),FileAllowed(['jpg','png'],'Images Only!')])
    submit = SubmitField('Submit')

class UserPic(FlaskForm):
    profile_pic = FileField('Upload a cover', validators=[FileRequired(),FileAllowed(['jpg','png'],'Images Only!')])
    submit = SubmitField('Enter')