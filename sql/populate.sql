-- Insert Users Active and passive ones. As well as an admin, Password is standard and just for testing
INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('admin.admin@hans-maier.de',
                                  'pbkdf2:sha256:50000$dLksb4c0$0815f5113091093c1250e9bd125a8ef6408527479e26d9799051ac172593987c',
                                  5, 1); 

INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('mueller.dieter@hans-maier.de',
                                  'pbkdf2:sha256:50000$reNWHZ3J$c0fb3ce1adb43618cca86d9ee6a5aa0259f0181fc8e94aa31863cfdb7988c560',
                                  4, 1);

INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('christoph.harmut@hans-maier.de',
                                  'pbkdf2:sha256:50000$Kk5u0M2L$29375937edd3af10e97462c34fc9062fd19bae4706bd3928f3d6f64558b58b88',
                                 4, 1);

INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('ingo.piller@hans-maier.de',
                                  'pbkdf2:sha256:50000$BQNdKFkM$a9cad9b47ccbe1db42b2c7495c344744b6401bc0a554aff8bfbb8fd491039ebb',
                                  4, 1);

INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('markus.meier@hans-maier.de',
                                  'pbkdf2:sha256:50000$JqsE2loF$eade84bd6c5fde737aac98aab215a7360ff56c87030338cbb8d44a6d4d6e03e5',
                                  4, 1);

INSERT INTO tralala.tralala_users (email, password, role_id, verified) VALUES ('hans.meier@hans-maier.de',
                                  'pbkdf2:sha256:50000$Aro4mlqB$1d436f29129578be8b07ba5e4598510c3758453a5c5c8c9111b7f555d5a044d3',
                                  4, 1);

-- Insert some random useless posts
INSERT INTO tralala.tralala_posts (uid, post_date, post_text, hashtags, upvotes, downvotes) VALUES (1, '2017-12-05 12:34:11', 'Ich hab nichts gemacht, das war schon so!', 'Kinder,stolen',
                                  10, 20);

INSERT INTO tralala.tralala_posts (uid, post_date, post_text, hashtags, upvotes, downvotes) VALUES (5, '2017-12-04 19:21:33', 'Sie sehen krank aus. Ich verschreibe Ihnen eine Pizza ', 'Essen,stolen', 400, 300);
