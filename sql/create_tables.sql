CREATE TABLE tralala_users(
	uid  INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role_id INT NOT NULL,
    verified BOOLEAN NOT NULL,
    verification_token varchar(100) NOT NULL,
    PRIMARY KEY (uid)
) ENGINE=INNODB;

CREATE TABLE tralala_roles(
	role_id INT NOT NULL AUTO_INCREMENT,
	role_name VARCHAR(100) NOT NULL UNIQUE,
	PRIMARY KEY (role_id),
	UNIQUE (role_name)
) ENGINE=INNODB;

CREATE TABLE tralala_posts(
	post_id INT NOT NULL AUTO_INCREMENT,
	uid INT,
	post_date DATETIME NOT NULL,
	post_text VARCHAR(280) NOT NULL,
	hashtags VARCHAR(280) NOT NULL,
	upvotes int NOT NULL,
	downvotes int NOT NULL,
	PRIMARY KEY (post_id)
) ENGINE=INNODB;