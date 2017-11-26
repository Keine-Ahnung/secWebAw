ALTER TABLE tralala_users ADD FOREIGN KEY (pid) REFERENCES tralala_profiles(pid) ON DELETE CASCADE;
ALTER TABLE tralala_posts ADD FOREIGN KEY (uid) REFERENCES tralala_users(uid) ON DELETE NO ACTION;