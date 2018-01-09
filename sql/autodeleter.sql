SET GLOBAL event_scheduler = ON;

SELECT @@event_scheduler;

use tralala;

CREATE EVENT AutoDeleteOldNotifications
ON SCHEDULE EVERY 5 MINUTE STARTS CURRENT_TIMESTAMP
ON COMPLETION PRESERVE
DO
DELETE LOW_PRIORITY FROM tralala.tralala_reset_password WHERE requesttime < TIMESTAMP(DATE_SUB(NOW(), INTERVAL 30 MINUTE));


CREATE EVENT AutoDeleteOldLogins
ON SCHEDULE EVERY 1 MINUTE STARTS CURRENT_TIMESTAMP
ON COMPLETION PRESERVE
DO
DELETE LOW_PRIORITY FROM tralala.tralala_login_attempts WHERE locktime < TIMESTAMP(DATE_SUB(NOW(), INTERVAL 10 MINUTE));
