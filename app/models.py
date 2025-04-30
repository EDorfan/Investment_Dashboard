from flask_login import UserMixin
from app.extensions import mysql

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
    

        

    
