# I'll explain the code line by line:
#
# 1. Import the FlaskForm class from flask_wtf
# 2. Import the StringField, PasswordField, and SubmitField classes from wtforms
# 3. Import the DataRequired, Email, and Length validators from wtforms.validators
# 4. Define the RegisterForm class that inherits from FlaskForm
# 5. Add a username field to the form with a DataRequired and Length validator
# 6. Add an email field to the form with a DataRequired and Email validator


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    ticker = StringField('Ticker', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    transaction_type = SelectField('Transaction Type', choices=[('buy', 'Buy'), ('sell', 'Sell')])
    transaction_date = DateField('Transaction Date', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

