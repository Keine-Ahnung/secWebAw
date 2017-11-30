# Tabellen
## tralala_users
* uid:`int` (PK)
* pid:`int` (FK -> profile.pid)
* role_id:`int` (FK -> roles.role_id)
* email:`varchar(100)`
* password:`varchar(40)`
* verified:`boolean`

## tralala_profiles
* pid:`int` (PK)
* prename:`varchar(20)`
* surname:`varchar(50)`

## tralala_roles
* role_id:`int` (PK)
* role_name:`varchar(100)`
* del_user:`boolean`
* set_role:`boolean`

## tralala_posts
* post_id:`int` (PK)
* uid:`int` (FK -> user.uid)
* timestamp:`datetime`
* post_text:`varchar(280)`
* hashtags:`varchar(280)`
* upvotes:`int`
* downvotes:`int`

# Constraints
## tralala_users -> tralala_profiles

`ON DELETE CASCADE`: Wenn ein User gelöscht wird, soll sein zugehöriges Profil automatisch auch gelöscht werden

## tralala_posts -> tralala_users

`ON DELETE NO ACTION`: Wenn ein Post gelöscht wird, soll der referenzierte User nicht gelöscht werden

# Zu klären

- [ ] tralala_posts.uid auf user.uid oder auf profile.pid?
