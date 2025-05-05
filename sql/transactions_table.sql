CREATE DATABASE IF NOT EXISTS Investment_DB;
USE Investment_DB;

-- Create the transactions table
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    quantity FLOAT NOT NULL,
    price DECIMAL(10, 4) NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    transaction_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

