# Tabellen
## tralala_users
* uid:`int` (PK)
* role_id:`int` (FK -> tralala_roles.role_id)
* email:`varchar(100)`
* password:`varchar(40)`
* verified:`boolean`

## tralala_roles
* role_id:`int` (PK)
* role_name:`varchar(100)`
* del_user:`boolean`
* set_role:`boolean`

## tralala_posts
* post_id:`int` (PK)
* uid:`int` (FK -> tralala_users.uid)
* timestamp:`datetime`
* post_text:`varchar(280)`
* hashtags:`varchar(280)`
* upvotes:`int`
* downvotes:`int`

## tralala_post_votes
* vote_id:`int` (PK)
* uid:`int` (FK -> tralala_users.uid)
* vote_date:`datetime`
* post_id`int` (FK -> tralala_posts.post_id)
* was_upvote:`boolean`
* was_downvote:`boolean`

## tralala_active_sessions
* session_id:`int` (PK)
* uid:`int` (FK -> tralala_user.uid)
* session_start:`datetime`
* session_max_alive:`datetime`

# Constraints
## tralala_users -> tralala_profiles

`ON DELETE CASCADE`: Wenn ein User gelöscht wird, soll sein zugehöriges Profil automatisch auch gelöscht werden

## tralala_posts -> tralala_users

`ON DELETE NO ACTION`: Wenn ein Post gelöscht wird, soll der referenzierte User nicht gelöscht werden

# Zu klären

- [ ] tralala_posts.uid auf user.uid oder auf profile.pid?
