-- Insert the Roles. 0 Admin 1 User
INSERT INTO tralala_roles VALUES ('Administrator');
INSERT INTO tralala_roles VALUES ('User');

-- Insert Users Active and passive ones. As well as an admin, Password is standard and just for testing
INSERT INTO tralala_users VALUES ('hans.meier@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  1, 1, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('Admin.admin@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  0, 1, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('mueller.dieter@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  1, 1, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('christoph.harmut@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                 1, 1, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('Ingo.piller@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  1, 1, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('markus.meier@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  0, 0, 'ichbinsowasvondermassensicher');

INSERT INTO tralala_users VALUES ('hans.meier@hans-maier.de',
                                  'dfb0396cc6d1a8078d76be64392e6bea166491cfe0cb8dc5e6e2f29e4917b665',
                                  1, 0, 'ichbinsowasvondermassensicher');

-- Insert some random useless posts
INSERT INTO tralala_posts VALUES (0, 'Ich hab nichts gemacht, das war schon so!' + CHAR(13)
                                     + CHAR(10) + '1.Kinder, die etwas angestellt haben.' + CHAR(13)
                                     + CHAR(10) +' 2. Eltern mit Computerproblemen', '#Kinder #stolen',
                                  10, 20);

INSERT INTO tralala_posts VALUES (1, 'Sie sehen krank aus. Ich verschreibe Ihnen eine Pizza ' + CHAR(13)
                                     + CHAR(10) + 'Dr. Oetker', '#Essen #stolen', 400, 300);
