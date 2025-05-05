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
    try:
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        # Add the transaction
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, ticker, quantity, price, transaction_type, transaction_date) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, ticker, quantity, price, transaction_type, transaction_date))
        
        # Add the price to stock_prices if it's a buy transaction
        if transaction_type == 'buy':
            cursor.execute("""
                INSERT INTO stock_prices 
                (ticker, price, timestamp) 
                VALUES (%s, %s, %s)
            """, (ticker, price, transaction_date))
        
        # Commit the transaction
        mysql.connection.commit()
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def get_all_transactions(user_id):
    # build out the connection
    cursor = mysql.connection.cursor()
    # aggregate quantity by ticker (find cumulative value and number of shares)
    cursor.execute("""
        WITH current_prices AS ( 
            SELECT 
                ticker,
                price AS current_price,
                timestamp AS last_price_update
            FROM stock_prices sp1
            WHERE timestamp = (
                SELECT MAX(timestamp)
                FROM stock_prices sp2
                WHERE sp2.ticker = sp1.ticker
            )
        ),

        current_holdings AS (
            SELECT 
                ticker,
                SUM(CASE WHEN transaction_type = 'buy' THEN quantity ELSE -quantity END) AS current_quantity
            FROM transactions
            WHERE user_id = %s
            GROUP BY ticker
            HAVING SUM(CASE WHEN transaction_type = 'buy' THEN quantity ELSE -quantity END) > 0
        ),

        ranked_transactions AS (
            SELECT 
                t.ticker,
                t.quantity,
                t.price,
                t.transaction_type,
                t.transaction_date,
                t.id,
                SUM(CASE 
                    WHEN t.transaction_type = 'buy' THEN t.quantity 
                    ELSE -t.quantity 
                END) OVER (
                    PARTITION BY t.ticker 
                    ORDER BY t.transaction_date DESC, t.id DESC
                ) AS running_total
            FROM transactions t
            WHERE t.user_id = %s
            AND t.transaction_type = 'buy'
        ),

        relevant_purchases AS (
            SELECT 
                rt.ticker,
                rt.quantity,
                rt.price,
                rt.running_total,
                ch.current_quantity,
                CASE 
                    WHEN rt.running_total <= ch.current_quantity THEN rt.quantity
                    ELSE rt.quantity - (rt.running_total - ch.current_quantity)
                END AS relevant_quantity
            FROM ranked_transactions rt
            JOIN current_holdings ch ON rt.ticker = ch.ticker
            WHERE rt.running_total > (rt.running_total - rt.quantity)
        )

        SELECT 
            t.ticker, 
            SUM(CASE WHEN t.transaction_type = 'buy' THEN t.quantity ELSE -t.quantity END) AS quantity, 
            SUM(CASE 
                WHEN t.transaction_type = 'buy' THEN -(t.quantity * t.price)
                ELSE (t.quantity * t.price)
            END) AS invested_value,
            cp.current_price,
            (SUM(CASE WHEN t.transaction_type = 'buy' THEN t.quantity ELSE -t.quantity END) * cp.current_price) AS current_value,
            cp.last_price_update,
            (
                SELECT SUM(rp.price * rp.relevant_quantity) / SUM(rp.relevant_quantity)
                FROM relevant_purchases rp
                WHERE rp.ticker = t.ticker
            ) AS avg_buy_price,
            CASE 
                WHEN cp.current_price IS NULL OR (
                    SELECT SUM(rp.price * rp.relevant_quantity) / SUM(rp.relevant_quantity)
                    FROM relevant_purchases rp
                    WHERE rp.ticker = t.ticker
                ) IS NULL THEN NULL
                WHEN (
                    SELECT SUM(rp.price * rp.relevant_quantity) / SUM(rp.relevant_quantity)
                    FROM relevant_purchases rp
                    WHERE rp.ticker = t.ticker
                ) > 0 THEN (
                    (cp.current_price - (
                        SELECT SUM(rp.price * rp.relevant_quantity) / SUM(rp.relevant_quantity)
                        FROM relevant_purchases rp
                        WHERE rp.ticker = t.ticker
                    )) / (
                        SELECT SUM(rp.price * rp.relevant_quantity) / SUM(rp.relevant_quantity)
                        FROM relevant_purchases rp
                        WHERE rp.ticker = t.ticker
                    ) * 100
                )
                ELSE 0
            END AS price_change_percentage
        FROM transactions t
        LEFT JOIN current_prices cp ON t.ticker = cp.ticker
        WHERE t.user_id = %s
        GROUP BY t.ticker, cp.current_price, cp.last_price_update
        HAVING SUM(CASE WHEN t.transaction_type = 'buy' THEN t.quantity ELSE -t.quantity END) != 0
    """, (user_id, user_id, user_id))
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

