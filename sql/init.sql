-- Initialize database
CREATE DATABASE IF NOT EXISTS bakery_database;

USE bakery_database;

-- Create tables
CREATE TABLE
    customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100) UNIQUE,
        phone_number VARCHAR(15),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        description TEXT,
        price DECIMAL(10, 2),
        in_stock BOOLEAN DEFAULT TRUE
    );

CREATE TABLE
    orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'pending', -- e.g., pending, paid, fulfilled
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );

CREATE TABLE
    orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'pending', -- e.g., pending, paid, fulfilled
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );

SELECT
    *
FROM
    orders
LIMIT
    1;