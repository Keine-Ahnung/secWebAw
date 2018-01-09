
-- Stored Proc: db_handler.get_all_posts()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_posts()
READS SQL DATA
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
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala_users (email, password, role_id, verified, verification_token) VALUES (p_email, p_pw, p_role_id, p_ver, p_ver_token);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_token_for_user()
DELIMITER $$

CREATE PROCEDURE tralala.get_token_for_user(
  IN p_email varchar(100)
)
READS SQL DATA
BEGIN
  SELECT verification_token from tralala.tralala_users WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_user_for_token()
DELIMITER $$

CREATE PROCEDURE tralala.get_user_for_token(
  IN p_token varchar(100)
)
READS SQL DATA
BEGIN
  SELECT email, verified from tralala.tralala_users WHERE verification_token = p_token;
END$$

DELIMITER ;

-- Stored Proc: db_handler.user_successful_verify()
DELIMITER $$

CREATE PROCEDURE tralala.user_successful_verify(
  IN p_email varchar(100)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_users  SET verified=1, role_id=4 WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.check_for_existence()
DELIMITER $$

CREATE PROCEDURE tralala.check_for_existence(
  IN p_email varchar(100)
)
READS SQL DATA
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
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_posts (uid, post_date, post_text, hashtags, upvotes, downvotes) VALUES (p_uid, p_post_date, p_post_text, p_hashtags, p_upvotes, p_downvotes);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_post_by_pid()
DELIMITER $$

CREATE PROCEDURE tralala.get_post_by_pid(
  IN p_pid int(11)
)
READS SQL DATA
BEGIN
  SELECT tralala_posts.post_id, tralala_users.email, tralala_posts.post_date, tralala_posts.post_text, tralala_posts.hashtags, tralala_posts.upvotes, tralala_posts.downvotes FROM tralala_posts INNER JOIN tralala_users ON tralala_posts.uid = tralala_users.uid WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.do_upvote()
DELIMITER $$

CREATE PROCEDURE tralala.do_upvote(
  IN p_pid int(11)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_posts SET upvotes = upvotes + 1 WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.do_downvote()
DELIMITER $$

CREATE PROCEDURE tralala.do_downvote(
  IN p_pid int(11)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_posts SET downvotes = downvotes + 1 WHERE post_id = p_pid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_all_users()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_users()
READS SQL DATA
BEGIN
  SELECT email, uid, role_id FROM tralala.tralala_users;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_all_roles()
DELIMITER $$

CREATE PROCEDURE tralala.get_all_roles()
READS SQL DATA
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
READS SQL DATA
BEGIN
  SELECT * FROM tralala.tralala_post_votes WHERE post_id = p_pid and uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.register_vote()
DELIMITER $$

CREATE PROCEDURE tralala.register_vote(
  IN p_uid int(11),
  IN p_vote_date datetime,
  IN p_post_id int(11),
  IN p_was_upvote tinyint(1),
  IN p_was_downvote tinyint(1)
)
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_post_votes (uid, vote_date, post_id, was_upvote, was_downvote) VALUES (p_uid, p_vote_date, p_post_id, p_was_upvote, p_was_downvote);
END$$

DELIMITER ;

-- Stored Proc: db_handler.start_session()
DELIMITER $$

CREATE PROCEDURE tralala.start_session(
  IN p_uid int(11),
  IN p_session_start datetime,
  IN p_session_max_alive datetime
)
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_active_sessions (uid, session_start, session_max_alive) VALUES (p_uid, p_session_start, p_session_max_alive);
END$$

DELIMITER ;

-- Stored Proc: db_handler.check_session_state()
DELIMITER $$

CREATE PROCEDURE tralala.check_session_state(
  IN p_uid int(11)
)
READS SQL DATA
BEGIN
  SELECT uid, session_max_alive FROM tralala.tralala_active_sessions WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.invalidate_session()
DELIMITER $$

CREATE PROCEDURE tralala.invalidate_session(
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  DELETE FROM tralala.tralala_active_sessions WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.delete_user()
DELIMITER $$

CREATE PROCEDURE tralala.delete_user(
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  DELETE FROM tralala.tralala_users WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_password_for_user()
DELIMITER $$

CREATE PROCEDURE tralala.get_password_for_user(
  IN p_email varchar(100)
)
READS SQL DATA
BEGIN
  SELECT password FROM tralala.tralala_users WHERE email = p_email;
END$$

DELIMITER ;

-- Stored Proc: db_handler.count_password_requests()
DELIMITER $$

CREATE PROCEDURE tralala.count_password_requests(
  IN p_uid int(11)
)
READS SQL DATA
BEGIN
  SELECT * FROM tralala.tralala_reset_password WHERE userid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.set_reset_token()
DELIMITER $$

CREATE PROCEDURE tralala.set_reset_token(
  IN p_uid int(11),
  IN p_token varchar(100),
  IN p_timestamp timestamp
)
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_reset_password VALUES (p_uid, p_token, p_timestamp);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_reset_token()
DELIMITER $$

CREATE PROCEDURE tralala.get_reset_token(
  IN p_uid int(11)
)
READS SQL DATA
BEGIN
  SELECT userid, token FROM tralala.tralala_reset_password WHERE userid = p_uid ORDER BY requesttime DESC;
END$$

DELIMITER ;

-- Stored Proc: db_handler.set_pass_for_user()
DELIMITER $$

CREATE PROCEDURE tralala.set_pass_for_user(
  IN p_password varchar(400),
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_users SET password = p_password WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.set_email_for_user()
DELIMITER $$

CREATE PROCEDURE tralala.set_email_for_user(
  IN p_email varchar(100),
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_users SET email = p_email WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.delete_pass_reset_token()
DELIMITER $$

CREATE PROCEDURE tralala.delete_pass_reset_token(
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  DELETE FROM tralala.tralala_reset_password WHERE userid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.set_token_password_change()
DELIMITER $$

CREATE PROCEDURE tralala.set_token_password_change(
  IN p_uid int(11),
  IN p_token varchar(100),
  IN p_timestamp timestamp,
  IN p_action varchar(50),
  IN p_password varchar(250)
)
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_cp_change VALUES (p_uid, p_token, p_timestamp, p_action, p_password);
END$$

DELIMITER ;

-- Stored Proc: db_handler.set_token_email_change
DELIMITER $$

CREATE PROCEDURE tralala.set_token_email_change(
  IN p_uid int(11),
  IN p_token varchar(100),
  IN p_timestamp timestamp,
  IN p_action varchar(50),
  IN p_email varchar(250)
)
MODIFIES SQL DATA
BEGIN
  INSERT INTO tralala.tralala_cp_change VALUES (p_uid, p_token, p_timestamp, p_action, p_email);
END$$

DELIMITER ;

-- Stored Proc: db_handler.get_reset_token_cp()
DELIMITER $$

CREATE PROCEDURE tralala.get_reset_token_cp(
  IN p_uid int(11),
  IN p_action varchar(50)
)
READS SQL DATA
BEGIN
  SELECT uid, token, data FROM tralala.tralala_cp_change WHERE uid = p_uid AND action = p_action ORDER BY requesttime DESC;
END$$

DELIMITER ;

-- Stored Proc: db_handler.delete_cp_token()
DELIMITER $$

CREATE PROCEDURE tralala.delete_cp_token(
  IN p_uid int(11),
  IN p_action varchar(50)
)
MODIFIES SQL DATA
BEGIN
  DELETE FROM tralala.tralala_cp_change WHERE uid = p_uid AND action = p_action;
END$$

DELIMITER ;

-- Stored Proc: db_handler.refresh_session_state
DELIMITER $$

CREATE PROCEDURE tralala.refresh_session_state(
  IN p_session_start datetime,
  IN p_session_max_alive datetime,
  IN p_uid int(11)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_active_sessions SET session_start = p_session_start, session_max_alive = p_session_max_alive WHERE uid = p_uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.check_user_locked()
DELIMITER $$

CREATE PROCEDURE tralala.check_user_locked(
  IN uid int(12)
)
READS SQL DATA
BEGIN
  SELECT uid, counter FROM tralala.tralala_login_attempts WHERE uid = uid;
END$$

DELIMITER ;

-- Stored Proc: db_handler.create_entry_user_locked()
DELIMITER $$

CREATE PROCEDURE tralala.create_entry_user_locked(
  IN uid int(12)
)
BEGIN
  INSERT INTO tralala.tralala_login_attempts (uid, counter) VALUES (uid, 1);
END$$

DELIMITER ;

-- Stored Proc: db_handler.iter_locked_counter()
DELIMITER $$

CREATE PROCEDURE tralala.iter_locked_counter(
  IN uid int(12)
)
MODIFIES SQL DATA
BEGIN
  UPDATE tralala.tralala_login_attempts SET counter = counter + 1 WHERE uid = uid;
END$$

DELIMITER ;
















