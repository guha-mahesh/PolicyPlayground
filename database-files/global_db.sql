DROP DATABASE IF EXISTS global_database;
CREATE DATABASE IF NOT EXISTS global_database;

USE global_database;


CREATE TABLE IF NOT EXISTS Policies (
    policy_id INT PRIMARY KEY,
    year_enacted INT
);

INSERT INTO Policies (policy_id, year_enacted) 
VALUES 
(1, 2000), (2, 1000);