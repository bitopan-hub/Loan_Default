CREATE DATABASE IF NOT EXISTS loan_default_db;
USE loan_default_db;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    PAN VARCHAR(10),
    dob DATE NOT NULL,
    occupation VARCHAR(100),
    period_of_service INT, -- in years
    RevolvingUtilizationOfUnsecuredLines FLOAT,
    age INT,
    `NumberOfTime30-59DaysPastDueNotWorse` INT,
    DebtRatio FLOAT,
    MonthlyIncome FLOAT,
    NumberOfOpenCreditLinesAndLoans INT,
    NumberOfTimes90DaysLate INT,
    NumberRealEstateLoansOrLines INT,
    `NumberOfTime60-89DaysPastDueNotWorse` INT,
    NumberOfDependents INT
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample admin user (password is 'admin123')
INSERT INTO users (full_name, email, phone, username, password) 
VALUES ('System Admin', 'admin@loan.com', '1234567890', 'admin', 'admin123');

-- Insert sample customers
INSERT INTO customers (
    name, dob, occupation, period_of_service, 
    RevolvingUtilizationOfUnsecuredLines, age, `NumberOfTime30-59DaysPastDueNotWorse`, 
    DebtRatio, MonthlyIncome, NumberOfOpenCreditLinesAndLoans, 
    NumberOfTimes90DaysLate, NumberRealEstateLoansOrLines, `NumberOfTime60-89DaysPastDueNotWorse`, 
    NumberOfDependents
) VALUES 
('Alice Smith', '1985-05-15', 'Software Engineer', 8, 
 0.7, 39, 0, 0.4, 60000, 5, 0, 1, 0, 2),
('Bob Jones', '1970-11-20', 'Sales Manager', 15, 
 0.95, 54, 2, 2.5, 45000, 12, 1, 2, 1, 1),
('Charlie Brown', '1992-02-10', 'Designer', 4, 
 0.2, 32, 0, 0.15, 30000, 3, 0, 0, 0, 0),
('Diana Prince', '1980-08-25', 'Director', 10, 
 0.1, 44, 0, 0.25, 120000, 8, 0, 2, 0, 3);
