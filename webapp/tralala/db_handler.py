from flask import Flask
from flaskext.mysql import MySQL
import time
import datetime
import security_helper
import traceback
from werkzeug.security import generate_password_hash, check_password_hash


class DB_Handler:
    db_connection_data = {}
    DB_TABLE_TRALALA_USERS = "tralala_users"
    DB_TABLE_TRALALA_POSTS = "tralala_posts"
    DB_TABLE_TRALALA_POST_VOTES = "tralala_post_votes"
    DB_TABLE_TRALALA_ACTIVE_SESSIONS = "tralala_active_sessions"
    DB_TABLE_TRALALA_ROLES = "tralala_roles"
    DB_TABLE_TRALALA_RESET_PASSWORD = "tralala_reset_password"
    DB_TABLE_TRALALA_CP_CHANGE = "tralala_cp_change"

    MAX_SESSION_TIME = 60  # Minuten

    def __init__(self):
        self.db_connection_data = None

    # if db_connection_data == None:
    #     self.db_connection_data["MYSQL_DATABASE_USER"] = "db_admin_tralala"
    #     self.db_connection_data["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
    #     self.db_connection_data["MYSQL_DATABASE_DB"] = "tralala"
    #     self.db_connection_data["MYSQL_DATABASE_HOST"] = "localhost"
    #     self.db_connection_data["DB_TABLE_TRALALA_USERS"] = "tralala_users"
    #
    # else:
    #     self.db_connection_data = db_connection_data

    def add_new_user(self, mysql, email, pw_hash, verification_token):
        """
        DB-Verbindung nach jedem Call wieder schließen

        1: User wurde angelegt
        0: User existiert bereits
        -1: User konnte nicht angelegt werden
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        pid = 1  # unverified
        role_id = 1  # unverified
        verified = 0

        record = [email.lower(), pw_hash, role_id, verified, verification_token]

        # Überprüfe ob User schon existiert
        cursor.execute("select email from " + self.DB_TABLE_TRALALA_USERS + " where email=%s", (email.lower(),))
        data = cursor.fetchone()

        if cursor.rowcount != 0:  # User existiert bereits
            return 0

        # Füge neuen User zur DB
        try:
            cursor.execute(
                "insert into " + self.DB_TABLE_TRALALA_USERS + " (email, password, role_id, verified, verification_token) values (%s,%s,%s,%s,%s)",
                record)
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            print(str(e))
            conn.close()
            return -1

    def get_token_for_user(self, mysql, email):
        """
        Gebe das Bestätigungstoken für eine E-Mail zurück.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select verification_token from " + self.DB_TABLE_TRALALA_USERS + " where email=%s", (email.lower(),))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            conn.close()

            return -1, "no_token"
        else:
            conn.close()
            return 1, data[0]

    def get_user_for_token(self, mysql, token):
        """
        Gebe den Benutzer basierend auf einem Bestätigungstoken zurück.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select email, verified from " + self.DB_TABLE_TRALALA_USERS + " where verification_token=%s", (token,))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_email"
        else:
            if data[1] == 1:  # wenn der Benutzer bereits bestätigt ist (verified=1)
                conn.close()
                return 2, data[0]
            else:
                return 1, data[0]

    def user_successful_verify(self, mysql, email):
        """
        Setze verified auf 1 und role_id auf 4 (verified) nach erfolgreicher Bestätigung des Accounts
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_USERS + " SET verified=1, role_id=4 WHERE email=%s", (email.lower(),))
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            print("Error bei user_successful_verify " + str(e))
            conn.close()
            return -1

    def check_for_existence(self, mysql, email):
        """
        Überprüfe anhand der E-Mail auf die Existenz eines Benutzers. Überprüfe ebenfalls, ob der Benutzer bestätigt ist.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select email, password, uid, role_id, verified from " + self.DB_TABLE_TRALALA_USERS + " where email=%s",
            (email.lower(),))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_user"
        elif data[4] == 0:
            return -2, "not_verified"
        else:
            conn.close()
            return 1, {"email": data[0], "password": data[1], "uid": data[2], "role_id": data[3], "verified": data[4]}

    def post_message_to_db(self, mysql, uid, email, text, hashtags):
        """
        Schreibe die neue Nachricht in die Datenbank. Die Nachricht als auch die Hashtags werden sanitized, um bösartigen
        Input zu unterbinden.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        post_date = time.strftime('%Y-%m-%d %H:%M:%S')

        cleaned_hashtags = security_helper.clean_hashtags(hashtags.strip())
        cleaned_text = security_helper.clean_messages(text)

        record = [uid, post_date, cleaned_text, cleaned_hashtags, 0, 0]

        try:
            cursor.execute(
                "INSERT INTO " + self.DB_TABLE_TRALALA_POSTS + " (uid, post_date, post_text, hashtags, upvotes, downvotes) VALUES (%s,%s,%s,%s,%s,%s)",
                record)

            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            conn.close()
            return -1

    def get_all_posts(self, mysql):
        """
        Gebe alls Posts als Liste zurück zurück.

        Indizes:
        - 0: post_id
        - 1: post_date
        - 2: post_text
        - 3: post_hashtags
        - 4: post_upvotes
        - 5: post_downvotes
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT tralala_posts.post_id, tralala_users.email, tralala_posts.post_date, tralala_posts.post_text, tralala_posts.hashtags, tralala_posts.upvotes, tralala_posts.downvotes FROM tralala_posts INNER JOIN tralala_users ON tralala_posts.uid = tralala_users.uid ORDER BY post_id DESC")
        data = cursor.fetchall()

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_posts"
        else:
            conn.close()
            return 1, data

    def get_post_by_pid(self, mysql, post_id):
        """
        Hole Post basierend auf einer spezifizierten Post-ID.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("SELECT * FROM " + self.DB_TABLE_TRALALA_POSTS + " WHERE post_id=%s", (post_id,))
        cursor.execute(
            "SELECT tralala_posts.post_id, tralala_users.email, tralala_posts.post_date, tralala_posts.post_text, tralala_posts.hashtags, tralala_posts.upvotes, tralala_posts.downvotes FROM tralala_posts INNER JOIN tralala_users ON tralala_posts.uid = tralala_users.uid WHERE post_id=%s",
            (post_id,))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_post"
        else:
            conn.close()
            return 1, data

    def do_upvote(self, mysql, post_id):
        """
        Registriere Upvote (inkrementiere Upvote-Wert eines Posts in der Tabelle um 1).
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_POSTS + " SET upvotes = upvotes + 1 WHERE post_id=%s", (post_id,))
            conn.commit()
            conn.close()
            return 1
        except:
            conn.close()
            return -1

    def do_downvote(self, mysql, post_id):
        """
        Registriere Downvote (inkrementiere Downvote-Wert eines Posts in der Tabelle um 1).

        Achtung: Der Downvotewert setzt sich folgendermaßen zusammen: downvote_real = upvote - downvote
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_POSTS + " SET downvotes = downvotes + 1 WHERE post_id=%s", (post_id,))
            conn.commit()
            conn.close()
            return 1
        except:
            conn.close()
            return -1

    def get_all_users(self, mysql):
        """
        Liefere alle Benutzer zurück.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select email, uid, role_id from " + self.DB_TABLE_TRALALA_USERS)
        data = cursor.fetchall()

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_user"
        else:
            conn.close()
            return 1, data

    def get_all_roles(self, mysql):
        """
        Liefere alle Rollen zurück.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "select role_id, role_name, del_user, set_role from " + self.DB_TABLE_TRALALA_ROLES)
            data = cursor.fetchall()
        except Exception as e:
            print(str(e))

        if cursor.rowcount == 0:
            conn.close()
            return -1, "no_roles"
        else:
            conn.close()
            return 1, data

    def check_if_already_voted(self, mysql, post_id, uid):
        """
        Überprüfe, ob ein Benutzer bereits für einen Post abgestimmt hat.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select * from " + self.DB_TABLE_TRALALA_POST_VOTES + " where post_id=%s and uid=%s",
            (post_id, uid,))
        data = cursor.fetchone()

        if not cursor.rowcount == 0:
            conn.close()
            return -1, "already_voted"
        else:
            conn.close()
            return 1, "not_voted_yet"

    def register_vote(self, mysql, post_id, uid, method):
        """
        Persistiere Vote des Benutzers.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        vote_date = time.strftime('%Y-%m-%d %H:%M:%S')
        was_upvote = 1 if method == "upvote" else 0
        was_downvote = 1 if method == "downvote" else 0

        record = [uid, vote_date, post_id, was_upvote, was_downvote]

        try:
            cursor.execute(
                "INSERT INTO " + self.DB_TABLE_TRALALA_POST_VOTES + " (uid, vote_date, post_id, was_upvote, was_downvote) VALUES (%s,%s,%s,%s,%s)",
                record)
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            conn.close()
            return -1

    def start_session(self, mysql, uid):
        """
        Trägt eine neue Session mit Startzeit und Endzeit in die Sessions-Tabelle ein (benötigt für automatischen Timeout).
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        session_start = datetime.datetime.now()
        session_max_alive = session_start + datetime.timedelta(minutes=self.MAX_SESSION_TIME)

        record = [uid, session_start, session_max_alive]

        try:
            cursor.execute(
                "INSERT INTO " + self.DB_TABLE_TRALALA_ACTIVE_SESSIONS + " (uid, session_start, session_max_alive) VALUES (%s, %s, %s)",
                record)

            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            conn.close()
            return -1

    def check_session_state(self, mysql, uid):
        """
        Überprüfe ob Session für Benutzer noch gültig ist.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        current_time = datetime.datetime.now()

        try:
            cursor.execute(
                "select uid, session_max_alive FROM " + self.DB_TABLE_TRALALA_ACTIVE_SESSIONS + " where uid=%s", (uid,))
            data = cursor.fetchone()

            if cursor.rowcount == 0:
                conn.commit()
                conn.close()
                return 0, "no_active_session_found_for_uid"
            else:
                session_max_alive = data[1]

            if current_time < session_max_alive:
                # return 1, "session_still_active"
                return 1, "times: now=" + str(current_time) + " max_active=" + str(session_max_alive)
            else:
                # return -1, "session_timeout"
                return -1, "times: now=" + str(current_time) + " max_active=" + str(session_max_alive)
        except Exception as e:
            conn.close()
            return -1, "current=" + str(current_time) + " FEHLER " + str(e)

    def invalidate_session(self, mysql, uid):
        """
        Lösche den Session-Eintrag des Benutzers aus der Sessions-Tabelle
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM " + self.DB_TABLE_TRALALA_ACTIVE_SESSIONS + " WHERE uid=%s", (uid,))
            conn.commit()
            conn.close()
            return 1, None
        except Exception as e:
            conn.close()
            return -1, e

    def delete_user(self, mysql, uid):
        """
        Lösche Benutzer.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM " + self.DB_TABLE_TRALALA_USERS + " WHERE uid=%s", (uid,))
            conn.commit()
            conn.close()
            return 1, None
        except Exception as e:
            conn.close()
            return -1, e

    def get_password_for_user(self, mysql, email):
        """
        Liefere Passwordhash für einen Benutzer zurück.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select password from " + self.DB_TABLE_TRALALA_USERS + " where email=%s",
            (email,))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            conn.close()
            return -1, False
        else:
            conn.close()
            return 1, data[0]

    def count_password_requests(self, mysql, uid, app):
        """
        Liefere die Anzahl bereits abgeschickter Passwort Resets zurück.
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "select * from " + self.DB_TABLE_TRALALA_RESET_PASSWORD + " where userid=%s",
            (uid,))
        data = cursor.fetchall()
        app.logger.debug("Total resets for " + str(uid) + ": " + str(cursor.rowcount))
        if cursor.rowcount >= 5:
            conn.close()
            return False
        else:
            conn.close()
            return True

    def set_reset_token(self, mysql, token, uid, app):
        """
        Registriere ein neues Reset Token für einen Passwortreset.
        """

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d %H:%M:%S')
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO " + self.DB_TABLE_TRALALA_RESET_PASSWORD + " VALUES (%s,%s,%s)",
                           (uid, token, timestamp,))
            conn.commit()
            conn.close()
        except Exception as e:
            app.logger.debug("Exception bei set_reset_token:\n" + str(e))
            conn.close()

    def get_reset_token(self, mysql, userid, mode=None):
        """
        Liefere das Token des aktuellsten Passwortrequest zurück.
        """

        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT userid, token FROM " + self.DB_TABLE_TRALALA_RESET_PASSWORD + " WHERE userid=%s ORDER BY requesttime DESC",
                (userid,))
            data = cursor.fetchall()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return None

            if mode == "get_token_uid":
                return data[0][0], data[0][1]

            return data[0][1]

        except Exception:
            conn.close()
            return None

    def set_pass_for_user(self, mysql, uid, new_pass, app):
        """
        Setze neues Passwort für einen Benutzer.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_USERS + " SET password=%s WHERE uid=%s", (new_pass, uid))
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            app.logger.debug("Fehler bei set_pass_for_user:\n" + str(e))
            conn.close()
            return -1

    def set_email_for_user(self, mysql, uid, new_email, app):
        """
        Setze neue E-Mail für einen Benutzer.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_USERS + " SET email=%s WHERE uid=%s", (new_email, uid))
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            app.logger.debug("Fehler bei set_email_for_user:\n" + str(e))
            conn.close()
            return -1

    def delete_pass_reset_token(self, mysql, uid, app):
        """
        Lösche alle Token vergangener Passwortrequests.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM " + self.DB_TABLE_TRALALA_RESET_PASSWORD + " WHERE userid=%s", (uid,))
            conn.commit()
            conn.close()
            return 1, None
        except Exception as e:
            app.logger.debug("Fehler bei delete_pass_reset_token:\n" + str(e))
            conn.close()
            return -1, e

    def set_token_password_change(self, mysql, uid, token, new_pass):
        """
        Registriere Token für Controlpanel Aktion (Passwort- oder E-Mailänderung).
        """

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d %H:%M:%S')
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO " + self.DB_TABLE_TRALALA_CP_CHANGE + " VALUES (%s,%s,%s,%s,%s)",
                           (uid, token, timestamp, "change_password", new_pass))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.close()

    def set_token_email_change(self, mysql, uid, token, new_email):
        """
        Setze Token für E-Mailänderung.
        """

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d %H:%M:%S')
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO " + self.DB_TABLE_TRALALA_CP_CHANGE + " VALUES (%s,%s,%s,%s,%s)",
                           (uid, token, timestamp, "change_email", new_email))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.close()

    def get_reset_token_cp(self, mysql, uid, action, mode=None, app=None):
        """
        Setze Token für Passwortänderung.
        """

        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT uid, token, data FROM " + self.DB_TABLE_TRALALA_CP_CHANGE + " WHERE uid=%s AND action=%s ORDER BY requesttime DESC",
                (uid, action))
            data = cursor.fetchall()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return None

            # Gebe das neue Passwort zurück, das nun in die Users-Tabelle geschrieben wird (spezieller Modus, um nicht zu viele einzelne Funktionen zu haben)
            if mode == "get_data":
                return data[0][2]
            # Gebe das Token zur Überprüfung zurück (eigentlicher Standardmodus)
            return data[0][1]

        except Exception as e:
            conn.close()
            if not app is None:
                app.logger.debug("Fehler bei get_reset_token_cp:\n" + str(e))
            return None

    def delete_cp_token(self, mysql, uid, action):
        """
        Lösche Token für Controlpanel Aktionen.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM " + self.DB_TABLE_TRALALA_CP_CHANGE + " WHERE uid=%s AND action=%s",
                           (uid, action))
            conn.commit()
            conn.close()
            return 1, None
        except Exception as e:
            conn.close()
            return -1, e

    def set_email_for_user(self, mysql, uid, new_email, app):
        """
        Setze neue E-Mail für Benutzer.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_USERS + " SET email=%s WHERE uid=%s", (new_email, uid))
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            app.logger.debug("Fehler bei set_email_for_user:\n" + str(e))
            conn.close()
            return -1

    def refresh_session_state(self, mysql, uid):
        """
        Refreshe die Session für den Benutzer.
        """

        conn = mysql.connect()
        cursor = conn.cursor()

        session_start = datetime.datetime.now()
        session_max_alive = session_start + datetime.timedelta(minutes=self.MAX_SESSION_TIME)

        try:
            cursor.execute(
                "UPDATE " + self.DB_TABLE_TRALALA_ACTIVE_SESSIONS + " SET session_start = %s, session_max_alive = %s WHERE uid = %s",
                (session_start, session_max_alive, uid))

            conn.commit()
            conn.close()
            return 1
            # return "refreshed session for " + str(uid) + " with session_start=" + str(session_start) + " session_max_alive=" + str(session_max_alive)
        except Exception as e:
            conn.close()
            return -1
            # return str(e)
