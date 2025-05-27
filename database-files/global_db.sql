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

CREATE TABLE IF NOT EXISTS `Foreign Aid` (
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

CREATE TABLE IF NOT EXISTS `US Interest Rates` (
    interest_id INT AUTO_INCREMENT PRIMARY KEY,
    fixed_rate INT,
    real_rate INT,
    rate_date DATE
)

CREATE TABLE IF NOT EXISTS ProposedPolicy (
    proposed_policy_id INT PRIMARY KEY,
    scope VARCHAR(20),
    enforcement VARCHAR(20),
    duration VARCHAR(20),
    FOREIGN KEY (country_id) REFERENCES Country(country_id)

);

CREATE TABLE HistoricalPolicy (
    historical_policy_id INT PRIMARY KEY,
    country_id INT,
    policy_name VARCHAR(100),
    description VARCHAR(255),
    category VARCHAR(100),
    date DATE,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

CREATE TABLE IF NOT EXISTS PolicyIdeas (
    entry_id INT PRIMARY KEY,
    percent_change INT,
    topic VARCHAR(200)
    FOREIGN KEY (entry_id) REFERENCES Conversations(convversation_id)

);

CREATE TABLE IF NOT EXISTS Conversations (
    convversation_id INT PRIMARY KEY,
    politican_id INT,
    content TEXT,
    FOREIGN KEY (politican_id) REFERENCES Politician(politican_id)

);

CREATE TABLE IF NOT EXISTS Politican (
    politican_id INT PRIMARY KEY,
    contact_info VARCHAR(250),
    name VARCHAR(250)
)