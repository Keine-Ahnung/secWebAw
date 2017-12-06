ALTER TABLE tralala.tralala_posts ADD FOREIGN KEY (uid) REFERENCES tralala_users(uid) ON DELETE NO ACTION;
ALTER TABLE tralala.tralala_users ADD FOREIGN KEY (role_id) REFERENCES tralala_roles(role_id) ON DELETE NO ACTION;

INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('anonymous', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('ad_bot', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('unverified', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('verified', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('administrator', '1', '1');

GRANT ALL PRIVILEGES ON tralala.* TO 'db_admin_tralala'@'localhost';
FLUSH PRIVILEGES;