-- create a database
CREATE DATABASE IF NOT EXISTS streamline_labs;
USE streamline_labs;

-- create contact message table
CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FLASE,
    ip_address VARCHAR(45),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read),
    INDEX idx_email (email)
);