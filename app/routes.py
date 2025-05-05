from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import mysql
from app.models import User, get_user_by_id, add_transaction, get_all_transactions, get_transaction_history, get_portfolio_history
from app.forms import RegisterForm, LoginForm, TransactionForm

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('A user with this email already exists. Please login instead.', 'warning')
            cur.close()
            return redirect(url_for('main.login'))
        
        # If user doesn't exist, proceed with registration
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (form.username.data, form.email.data, form.password.data))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                    (form.email.data, form.password.data))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            user = User(*user_data)
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Routes to add personal transactions and display them
@main.route('/personal_portfolio', methods=['GET', 'POST'])
@login_required
def personal_portfolio():
    form = TransactionForm()
    if form.validate_on_submit():
        add_transaction(
            current_user.id, 
            form.ticker.data.upper(), 
            form.quantity.data,
            form.price.data,
            form.transaction_type.data, 
            form.transaction_date.data
        )
        flash('Transaction added successfully', 'success')
        return redirect(url_for('main.personal_portfolio'))
    holdings = get_all_transactions(current_user.id)
    history = get_transaction_history(current_user.id)
    portfolio_history = get_portfolio_history(current_user.id)
    return render_template('personal_portfolio.html', 
                         form=form, 
                         holdings=holdings, 
                         history=history,
                         portfolio_history=portfolio_history)