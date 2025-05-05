CREATE TABLE IF NOT EXISTS stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    timestamp DATETIME NOT NULL,
    UNIQUE KEY unique_ticker_time (ticker, timestamp)
); 

