CREATE DATABASE IF NOT EXISTS Investment_DB;

USE Investment_DB;

CREATE TABLE stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10),
    date DATE,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT,
    volume BIGINT
);
