
-- Stored Proc: db_handler.get_all_posts()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_posts()
BEGIN
  SELECT tralala_posts.post_id, tralala_users.email, tralala_posts.post_date, tralala_posts.post_text, tralala_posts.hashtags, tralala_posts.upvotes, tralala_posts.downvotes FROM tralala_posts INNER JOIN tralala_users ON tralala_posts.uid = tralala_users.uid ORDER BY post_id DESC;
END$$

DELIMITER ;

-- Stored Proc: db_handler.add_new_user()
DELIMITER $$

CREATE PROCEDURE tralala.add_new_user(
  IN p_email varchar(100),
  IN p_pw varchar(400),
  IN p_role_id int(11),
  IN p_ver tinyint(1),
  p_ver_token varchar(100)
)
BEGIN
  INSERT INTO tralala_users (email, password, role_id, verified, verification_token) VALUES (p_email, p_pw, p_role_id, p_ver, p_ver_token);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_token_for_user()
DELIMITER $$

CREATE PROCEDURE tralala.get_token_for_user(
  IN p_email varchar(100)
)
BEGIN
  SELECT verification_token from tralala.tralala_users WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_user_for_token()
DELIMITER $$

CREATE PROCEDURE tralala.get_user_for_token(
  IN p_token varchar(100)
)
BEGIN
  SELECT email, verified from tralala.tralala_users WHERE verification_token = p_token;
END$$

DELIMITER ;

-- Stored Proc: db_handler.user_successful_verify()
DELIMITER $$

CREATE PROCEDURE tralala.user_successful_verify(
  IN p_email varchar(100)
)
BEGIN
  UPDATE tralala.tralala_users  SET verified=1, role_id=4 WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.check_for_existence()
DELIMITER $$

CREATE PROCEDURE tralala.check_for_existence(
  IN p_email varchar(100)
)
BEGIN
  SELECT email, password, uid, role_id, verified FROM tralala.tralala_users WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.post_message_to_db()
DELIMITER $$

CREATE PROCEDURE tralala.post_message_to_db(
  IN p_uid int(11),
  IN p_post_date datetime,
  IN p_post_text varchar(280),
  IN p_hashtags varchar(280),
  IN p_upvotes int(11),
  IN p_downvotes int(11)
)
BEGIN
  INSERT INTO tralala.tralala_posts (uid, post_date, post_text, hashtags, upvotes, downvotes) VALUES (p_uid, p_post_date, p_post_text, p_hashtags, p_upvotes, p_downvotes);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_post_by_pid()
DELIMITER $$

CREATE PROCEDURE tralala.get_post_by_pid(
  IN p_pid int(11)
)
BEGIN
  SELECT tralala_posts.post_id, tralala_users.email, tralala_posts.post_date, tralala_posts.post_text, tralala_posts.hashtags, tralala_posts.upvotes, tralala_posts.downvotes FROM tralala_posts INNER JOIN tralala_users ON tralala_posts.uid = tralala_users.uid WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.do_upvote()
DELIMITER $$

CREATE PROCEDURE tralala.do_upvote(
  IN p_pid int(11)
)
BEGIN
  UPDATE tralala.tralala_posts SET upvotes = upvotes + 1 WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.do_downvote()
DELIMITER $$

CREATE PROCEDURE tralala.do_downvote(
  IN p_pid int(11)
)
BEGIN
  UPDATE tralala.tralala_posts SET downvotes = downvotes + 1 WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_all_users()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_users()
BEGIN
  SELECT email, uid, role_id FROM tralala.tralala_users;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_all_roles()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_roles()
BEGIN
  SELECT role_id, role_name, del_user, set_role FROM tralala.tralala_roles;
END$$

DELIMITER ;

-- Stored Proc: db_handler.check_if_already_voted()
DELIMITER $$

CREATE PROCEDURE tralala.check_if_already_voted(
  IN p_pid int(11),
  IN p_uid int(11)
)
BEGIN
  SELECT * FROM tralala.tralala_post_votes WHERE post_id = p_pid and uid = p_uid;
END$$

DELIMITER ;






















