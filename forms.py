from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField, validators, SelectMultipleField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import TextArea

class AddDish(FlaskForm):
    name = StringField('Dish Name: ', validators=[InputRequired()])
    cost = IntegerField('Dish Price', validators=[InputRequired()])
    cookTime= IntegerField('Cook Time', validators=[InputRequired()])
    dishType = StringField('Dish type:',validators=[InputRequired()])
    dishDescription = TextAreaField('Dish Description: ')
    #allergins= TextAreaField('Add any allergins that are applicable: ')
    allergins=SelectMultipleField('Allergins:', choices=[('gluten','Gluten'),('dairy','Dairy'),('nut','Nut'),('soya','soya'),('egg','Egg')])
    dishPic = FileField('Upload a picture of dish:',validators=[FileRequired(),FileAllowed(['jpg','png'],'Images Only!')])
    ingredients= TextAreaField('Add ingredients necessary for this dish',default="In the format ingredient1,ingredient2, pls separte with a comma!")
    submit = SubmitField('Submit')

class UserPic(FlaskForm):
    profile_pic = FileField('Upload a cover', validators=[FileRequired(),FileAllowed(['jpg','png'],'Images Only!')])
    submit = SubmitField('Enter')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired("Email doesn't exist")])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    name = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class ReplyForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    subject = StringField(validators=[InputRequired()])
    submit = SubmitField("Send message")

class EmployeeForm(FlaskForm):
    first_name = StringField("First name: ", default="", validators=[InputRequired()])
    last_name = StringField("Last name: ", default="", validators=[InputRequired()])
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    role = StringField("Role: ", default="", validators=[InputRequired()])
    access_level = SelectField("Choose an option", 
                                        choices = [("managerial", "Managerial"),
                                                    ("ordinary staff", "Ordinary staff")], validators=[InputRequired()])
    submit = SubmitField("Create")

class NewPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm new password", validators=[InputRequired("Password doesn't match"), EqualTo("new_password")])
    submit = SubmitField("Change password")

class ResetPasswordForm(FlaskForm):
    role = RadioField("Are you a...", 
    choices = [("customer", "Customer"),
                ("staff", "Staff member")], validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired("Please fill in an email address")])
    submit = SubmitField("Change password")

class CodeForm(FlaskForm):
    code = StringField('Enter the 5 digit code here', validators=[InputRequired("Wrong code")])
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")

class cardDetails(FlaskForm):
    cardNum = IntegerField('Enter card number:', validators=[InputRequired()])
    cardHolder = StringField('Enter card holders name:', validators=[InputRequired()])
    cvv = IntegerField('Cvv', validators= [InputRequired()])
    submit = SubmitField('Enter')

class submitModifications(FlaskForm):
    submit = SubmitField('Enter')