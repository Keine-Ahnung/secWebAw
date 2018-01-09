ALTER TABLE tralala.tralala_posts ADD FOREIGN KEY (uid) REFERENCES tralala.tralala_users(uid) ON DELETE CASCADE;
ALTER TABLE tralala.tralala_users ADD FOREIGN KEY (role_id) REFERENCES tralala.tralala_roles(role_id) ON DELETE NO ACTION;
ALTER TABLE tralala.tralala_post_votes ADD FOREIGN KEY (uid) REFERENCES tralala.tralala_users(uid) ON DELETE NO ACTION;
ALTER TABLE tralala.tralala_post_votes ADD FOREIGN KEY (post_id) REFERENCES tralala.tralala_posts(post_id) ON DELETE NO ACTION;
ALTER TABLE tralala.tralala_active_sessions ADD FOREIGN KEY (uid) REFERENCES tralala.tralala_users(uid) ON DELETE NO ACTION;
ALTER TABLE tralala.tralala_reset_password ADD FOREIGN KEY (userid) REFERENCES tralala.tralala_users(uid) ON DELETE CASCADE;
ALTER TABLE tralala.tralala_cp_change ADD FOREIGN KEY (uid) REFERENCES tralala.tralala_users(uid) ON DELETE CASCADE;
ALTER TABLE tralala.tralala_login_attempts ADD FOREIGN KEY (uid) REFERENCES tralala.tralala_users(uid) ON DELETE CASCADE;


INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('anonymous', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('ad_bot', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('unverified', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('verified', '0', '0');
INSERT INTO tralala.tralala_roles (role_name, del_user, set_role) VALUES ('administrator', '1', '1');

GRANT ALL PRIVILEGES ON tralala.* TO 'db_admin_tralala'@'localhost';
FLUSH PRIVILEGES;