DROP DATABASE IF EXISTS global_database;
CREATE DATABASE IF NOT EXISTS global_database;

USE global_database;


CREATE TABLE IF NOT EXISTS Countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Education (
    education_id INT AUTO_INCREMENT PRIMARY KEY,
    amount INT,
    country_id INT,
    policy_date DATE,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id)
);

CREATE TABLE IF NOT EXISTS Foreign Aid (
    aid_id INT AUTO_INCREMENT PRIMARY KEY,
    amount INT,
    country_id INT,
    policy_date DATE,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id)
);

CREATE TABLE IF NOT EXISTS Trade (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    exports INT,
    imports INT,
    country_id INT,
    policy_date DATE,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id)
);

CREATE TABLE IF NOT EXISTS Currencies (
    currency_id INT AUTO_INCREMENT PRIMARY KEY,
    conversion_rate INT,
    country_id INT,
    exchange_date DATE,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id)
);