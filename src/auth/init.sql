CREATE USER 'auth_service'@'localhost' IDENTIFIED BY '1234324fefwsedf';

CREATE DATABASE auth;

GRANT ALL PRIVILEGES ON auth.* TO 'auth_service'@'localhost';

USE auth;

CREATE TABLE user(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user (email, password) VALUES ('alieksieiev.yurii@gmail.com', '1234')