DROP DATABASE IF EXISTS global_database;
CREATE DATABASE IF NOT EXISTS global_database;

USE global_database;

CREATE TABLE IF NOT EXISTS Countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS UserTypes (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS Interest (
    interest_id INT AUTO_INCREMENT PRIMARY KEY,
    interest_name VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    type_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    interest_id INT,
    FOREIGN KEY (type_id) REFERENCES UserTypes(type_id),
    FOREIGN KEY (interest_id) REFERENCES Interest(interest_id)
);

CREATE TABLE IF NOT EXISTS SavedPolicy (
    saved_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    frdr INT,
    fbss INT,
    tsh INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS SP500 (
    sp_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    close DECIMAL(10, 5)
);

CREATE TABLE IF NOT EXISTS GDPUS (
    gdpus_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    close DECIMAL(10, 5)
);

CREATE TABLE IF NOT EXISTS GDPWORLD (
    gdpworld_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    close DECIMAL(10, 5)
);

CREATE TABLE IF NOT EXISTS URTH (
    urth_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    close DECIMAL(10, 5)
);

CREATE TABLE IF NOT EXISTS ProposedPolicy (
    proposed_policy_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    scope VARCHAR(20),
    enforcement VARCHAR(20),
    duration VARCHAR(20),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE HistoricalPolicy (
    historical_policy_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    country_id INT,
    policy_name VARCHAR(100),
    description VARCHAR(255),
    category VARCHAR(100),
    date DATE,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Politicians (
    politician_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    contact_info VARCHAR(250),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Conversations (
    conversation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    politician_id INT,
    saved_id INT,
    content TEXT,
    title VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    -- FOREIGN KEY (saved_id) REFERENCES SavedPolicy(saved_id),
    FOREIGN KEY (politician_id) REFERENCES Politicians(politician_id)
);

INSERT INTO UserTypes (type_name)
VALUES
('admin'),
('policy_maker'),
('lobbyist'),
('economist');

INSERT INTO Interest (interest_name)
VALUES
('monetary'),
('fiscal'),
('other');

INSERT INTO Users (type_id, first_name, last_name, interest_id)
VALUES
(1, 'Sota', 'Shimizu', 3),
(3, 'Eleanor', 'Goossens', 2);

INSERT INTO Politicians (name, contact_info, user_id)
VALUES
('John Pork', '123-456-7890', 2);