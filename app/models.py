from flask_login import UserMixin
from app.extensions import mysql
from collections import namedtuple

class User(UserMixin):
    
    # This class represents a User in the system, inheriting from UserMixin for Flask-Login functionality
    # The __init__ method initializes a new User with:
    #   - id: unique identifier for the user
    #   - username: user's display name
    #   - email: user's email address
    #   - password: user's hashed password
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
    
# The get_user_by_id method is a class method that:
#   - Takes a user_id parameter
#   - Creates a database cursor
#   - Executes a SQL query to find a user by their ID
#   - Fetches the result and closes the cursor
#   - Returns a new User instance with the database values
def get_user_by_id(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return User(user[0], user[1], user[2], user[3])

# Function to add new transactions to database based off own users information
def add_transaction(user_id, ticker, quantity, price, transaction_type, transaction_date):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO transactions (user_id, ticker, quantity, price, transaction_type, transaction_date) VALUES (%s, %s, %s, %s, %s, %s)",
                   (user_id, ticker, quantity, price, transaction_type, transaction_date))
    mysql.connection.commit()
    cursor.close()

def get_all_transactions(user_id):
    # build out the connection
    cursor = mysql.connection.cursor()
    # aggregate quantity by ticker (find cumulative value and number of shares)
    cursor.execute("""
        SELECT 
            ticker, 
            SUM(CASE WHEN transaction_type = 'buy' THEN quantity ELSE -quantity END) AS quantity, 
            SUM(CASE 
                WHEN transaction_type = 'buy' THEN -(quantity * price)
                ELSE (quantity * price)
            END) AS value,
            MAX(transaction_date) as last_transaction_date
        FROM transactions
        WHERE user_id = %s
        GROUP BY ticker
        HAVING SUM(CASE WHEN transaction_type = 'buy' THEN quantity ELSE -quantity END) != 0
    """, (user_id,))
    transactions = cursor.fetchall()
    cursor.close()
    return transactions

def get_transaction_history(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            ticker,
            quantity,
            price,
            transaction_type,
            transaction_date,
            CASE 
                WHEN transaction_type = 'buy' THEN -(quantity * price)
                ELSE (quantity * price)
            END as value
        FROM transactions
        WHERE user_id = %s
        ORDER BY transaction_date DESC
    """, (user_id,))
    history = cursor.fetchall()
    cursor.close()
    return history
