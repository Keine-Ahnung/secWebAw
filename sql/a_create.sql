DROP DATABASE IF EXISTS tralala;

CREATE DATABASE tralala;

CREATE TABLE tralala.tralala_users(
	uid  INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(400) NOT NULL,
    role_id INT NOT NULL,
    verified BOOLEAN NOT NULL,
    verification_token varchar(100),
    PRIMARY KEY (uid)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_roles(
	role_id INT NOT NULL AUTO_INCREMENT,
	role_name VARCHAR(100) NOT NULL UNIQUE,
	del_user BOOLEAN,
	set_role BOOLEAN,
	PRIMARY KEY (role_id),
	UNIQUE (role_name)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_posts(
	post_id INT NOT NULL AUTO_INCREMENT,
	uid INT,
	post_date DATETIME NOT NULL,
	post_text VARCHAR(280) NOT NULL,
	hashtags VARCHAR(280) NOT NULL,
	upvotes int NOT NULL,
	downvotes int NOT NULL,
	PRIMARY KEY (post_id)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_post_votes(
	vote_id INT NOT NULL AUTO_INCREMENT,
	uid INT,
	vote_date DATETIME NOT NULL,
	post_id INT NOT NULL,
	was_upvote BOOLEAN NOT NULL,
	was_downvote BOOLEAN NOT NULL,
	PRIMARY KEY (vote_id)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_active_sessions(
	session_id INT NOT NULL AUTO_INCREMENT,
	uid INT,
	session_start DATETIME NOT NULL,
	session_max_alive DATETIME NOT NULL,
	PRIMARY KEY (session_id)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_reset_password(
	userid INT NOT NULL,
	token varchar(100) NOT NULL UNIQUE,
	requesttime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (userid)
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_cp_change(
	uid INT NOT NULL,
	token varchar(100) NOT NULL UNIQUE,
	requesttime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	action varchar(50) NOT NULL,
	data varchar(250) NOT NULL
) ENGINE=INNODB;

CREATE TABLE tralala.tralala_login_attempts(
  uid INT NOT NULL,
  counter INT NOT NULL,
  locktime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (uid)
)ENGINE=INNODB;


DROP USER IF EXISTS 'db_admin_tralala'@'localhost', 'db_admin_tralala'@'%';
FLUSH PRIVILEGES;
CREATE USER 'db_admin_tralala'@'localhost' IDENTIFIED BY 'tr4l4l4_mysql_db.';