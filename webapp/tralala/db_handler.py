from flask import Flask
from flaskext.mysql import MySQL
import time
import datetime
import security_helper
import traceback
from werkzeug.security import generate_password_hash, check_password_hash


__MAX_SESSION_TIME = 60  # Minuten


def add_new_user(mysql, email, pw_hash, verification_token):
    """
    DB-Verbindung nach jedem Call wieder schließen

    1: User wurde angelegt
    0: User existiert bereits
    -1: User konnte nicht angelegt werden
    """
    cursor = mysql.cursor()

    ROLE_ID = 1  # unverified
    VERIFIED = 0

    # Überprüfe ob User schon existiert
    cursor.callproc("tralala.check_for_existence", (email.lower(),))

    if cursor.rowcount != 0:  # User existiert bereits
        return 0

    else:
        try:
            cursor.callproc("tralala.add_new_user", (email.lower(), pw_hash,
                                                     ROLE_ID, VERIFIED,
                                                     verification_token))
            mysql.commit()
            return 1

        except Exception as e:
            print(str(e))
            return -1


def get_token_for_user(mysql, email):
    """
    Gebe das Bestätigungstoken für eine E-Mail zurück.
    """
    cursor = mysql.cursor()

    cursor.callproc("tralala.get_token_for_user", (email.lower(),))
    data = cursor.fetchone()

    if cursor.rowcount == 0:
        return -1, "no_token"

    else:
        return 1, data[0]


def get_user_for_token(mysql, token):
    """
    Gebe den Benutzer basierend auf einem Bestätigungstoken zurück.
    """
    cursor = mysql.cursor()

    cursor.callproc("tralala.get_user_for_token", (token,))
    data = cursor.fetchone()

    if cursor.rowcount == 0:
        return -1, "no_email"

    else:
        if data[1] == 1:
            # wenn der Benutzer bereits bestätigt ist (verified=1)
            return 2, data[0]

        else:
            return 1, data[0]


def user_successful_verify(mysql, email):
    """
    Setze verified auf 1 und role_id auf 4 (verified) nach
    erfolgreicher Bestätigung des Accounts
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("user_successful_verify", (email.lower(),))
        mysql.commit()
        return 1

    except Exception as e:
        print("Error bei user_successful_verify " + str(e))
        return -1


def check_for_existence(mysql, email):
    """
    Überprüfe anhand der E-Mail auf die Existenz eines Benutzers.
    Überprüfe ebenfalls, ob der Benutzer bestätigt ist.
    """
    cursor = mysql.cursor()
    cursor.callproc("tralala.check_for_existence", (email.lower(),))
    data = cursor.fetchone()

    if cursor.rowcount == 0:
        return -1, "no_user"

    elif data[4] == 0:
        return -2, "not_verified"

    else:
        return 1, {"email": data[0], "password": data[1],
                   "uid": data[2], "role_id": data[3], "verified": data[4]}


def post_message_to_db(mysql, uid, email, text, hashtags):
    """
    Schreibe die neue Nachricht in die Datenbank. Die Nachricht als auch
    die Hashtags werden sanitized, um bösartigen
    Input zu unterbinden.
    """
    cursor = mysql.cursor()
    post_date = time.strftime('%Y-%m-%d %H:%M:%S')
    cleaned_hashtags = security_helper.clean_hashtags(hashtags.strip())
    cleaned_text = security_helper.clean_messages(text)

    try:
        cursor.callproc("post_message_to_db", (uid, post_date, cleaned_text,
                                               cleaned_hashtags, 0, 0))

        mysql.commit()
        return 1

    except Exception as e:
        return -1


def get_all_posts(mysql):
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
    cursor = mysql.cursor()
    cursor.callproc("tralala.get_all_posts")
    data = cursor.fetchall()

    if cursor.rowcount == 0:
        return -1, "no_posts"

    else:
        return 1, data


def get_post_by_pid(mysql, post_id):
    """
    Hole Post basierend auf einer spezifizierten Post-ID.
    """
    cursor = mysql.cursor()
    cursor.callproc("get_post_by_pid", (post_id,))
    data = cursor.fetchone()

    if cursor.rowcount == 0:
        return -1, "no_post"

    else:
        return 1, data


def do_upvote(mysql, post_id):
    """
    Registriere Upvote (inkrementiere Upvote-Wert eines
    Posts in der Tabelle um 1).
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("do_upvote", (post_id,))
        mysql.commit()
        return 1

    except Exception as e:
        return -1



def do_downvote(mysql, post_id):
    """
    Registriere Downvote (inkrementiere Downvote-Wert
    eines Posts in der Tabelle um 1).

    Achtung: Der Downvotewert setzt sich folgendermaßen
    zusammen: downvote_real = upvote - downvote
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("do_downvote", (post_id,))
        mysql.commit()
        return 1

    except Exception as e:
        return -1


def get_all_users(mysql):
    """
    Liefere alle Benutzer zurück.
    """
    cursor = mysql.cursor()

    cursor.callproc("get_all_users")
    data = cursor.fetchall()

    if cursor.rowcount == 0:
        return -1, "no_user"

    else:
        return 1, data


def get_all_roles(mysql):
    """
    Liefere alle Rollen zurück.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("get_all_roles")
        data = cursor.fetchall()

        if cursor.rowcount == 0:
            return -1, "no_roles"

        else:
            return 1, data

    except Exception as e:
        print(str(e))


def check_if_already_voted(mysql, post_id, uid):
    """
    Überprüfe, ob ein Benutzer bereits für einen Post abgestimmt hat.
    """
    cursor = mysql.cursor()
    cursor.callproc("check_if_already_voted", (post_id, uid,))

    if not cursor.rowcount == 0:
        return -1, "already_voted"

    else:
        return 1, "not_voted_yet"


def register_vote(mysql, post_id, uid, method):
    """
    Persistiere Vote des Benutzers.
    """
    cursor = mysql.cursor()
    vote_date = time.strftime('%Y-%m-%d %H:%M:%S')
    was_upvote = 1 if method == "upvote" else 0
    was_downvote = 1 if method == "downvote" else 0

    try:
        cursor.callproc("register_vote", (uid, vote_date, post_id,
                                          was_upvote, was_downvote))
        mysql.commit()
        return 1

    except Exception as e:
        return -1


def start_session(mysql, uid):
    """
    Trägt eine neue Session mit Startzeit und Endzeit in die Sessions-
    Tabelle ein (benötigt für automatischen Timeout).
    """
    cursor = mysql.cursor()
    session_start = datetime.datetime.now()
    session_max_alive = session_start \
                        + datetime.timedelta(minutes=__MAX_SESSION_TIME)

    try:
        cursor.callproc("start_session", (uid, session_start, session_max_alive,))
        mysql.commit()
        return 1
    except Exception as e:
        return -1


def check_session_state(mysql, uid):
    """
    Überprüfe ob Session für Benutzer noch gültig ist.
    """
    cursor = mysql.cursor()
    current_time = datetime.datetime.now()

    try:
        cursor.callproc("check_session_state", (uid,))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            mysql.commit()
            return 0, "no_active_session_found_for_uid"

        else:
            session_max_alive = data[1]

        if current_time < session_max_alive:
            # return 1, "session_still_active"
            return 1, "times: now=" + str(current_time) + " max_active="\
                   + str(session_max_alive)

        else:
            # return -1, "session_timeout"
            return -1, "times: now=" + str(current_time) + " max_active="\
                   + str(session_max_alive)

    except Exception as e:
        return -1, "current=" + str(current_time) + " FEHLER " + str(e)


def invalidate_session(mysql, uid):
    """
    Lösche den Session-Eintrag des Benutzers aus der Sessions-Tabelle
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("invalidate_session", (uid,))
        mysql.commit()
        return 1, None

    except Exception as e:
        return -1, e


def delete_user(mysql, uid):
    """
    Lösche Benutzer.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("delete_user", (uid,))
        mysql.commit()
        return 1, None

    except Exception as e:
        return -1, e


def get_password_for_user(mysql, email):
    """
    Liefere Passwordhash für einen Benutzer zurück.
    """
    cursor = mysql.cursor()
    cursor.callproc("get_password_for_user", (email.lower(),))
    data = cursor.fetchone()

    if cursor.rowcount == 0:
        return -1, False

    else:
        return 1, data[0]

#think about a better solution
def count_password_requests(mysql, uid, app):
    """
    Liefere die Anzahl bereits abgeschickter Passwort Resets zurück.
    """
    cursor = mysql.cursor()
    cursor.callproc("count_password_requests", (uid,))
    app.logger.debug("Total resets for " + str(uid)
                     + ": " + str(cursor.rowcount))

    if cursor.rowcount >= 5:
        return False

    else:
        return True


def set_reset_token(mysql, token, uid, app):
    """
    Registriere ein neues Reset Token für einen Passwortreset.
    """
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y-%m-%d %H:%M:%S')
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_reset_token", (uid, token, timestamp,))
        mysql.commit()

    except Exception as e:
        app.logger.debug("Exception bei set_reset_token:\n" + str(e))


def get_reset_token(mysql, userid, mode=None):
    """
    Liefere das Token des aktuellsten Passwortrequest zurück.
    """
    cursor = mysql.cursor()
    try:
        cursor.callproc("get_reset_token", (userid,))
        data = cursor.fetchall()

        if cursor.rowcount == 0:
            cursor.close()
            return None

        if mode == "get_token_uid":
            return data[0][0], data[0][1]

        return data[0][1]

    except Exception:
        return None


def set_pass_for_user(mysql, uid, new_pass, app):
    """
    Setze neues Passwort für einen Benutzer.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_pass_for_user", (new_pass, uid,))
        mysql.commit()
        return 1

    except Exception as e:
        app.logger.debug("Fehler bei set_pass_for_user:\n" + str(e))
        return -1


def set_email_for_user(mysql, uid, new_email, app):
    """
    Setze neue E-Mail für einen Benutzer.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_email_for_user", (new_email, uid,))
        mysql.commit()
        return 1

    except Exception as e:
        app.logger.debug("Fehler bei set_email_for_user:\n" + str(e))
        return -1


def delete_pass_reset_token(mysql, uid, app):
    """
    Lösche alle Token vergangener Passwortrequests.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("delete_pass_reset_token", (uid,))
        mysql.commit()
        return 1, None

    except Exception as e:
        app.logger.debug("Fehler bei delete_pass_reset_token:\n" + str(e))
        return -1, e


def set_token_password_change(mysql, uid, token, new_pass):
    """
    Registriere Token für Controlpanel Aktion (Passwort-
    oder E-Mailänderung).
    """
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y-%m-%d %H:%M:%S')
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_token_password_change", (uid, token,
                                                      timestamp,
                                                      "change_password",
                                                      new_pass,))
        mysql.commit()

    except Exception as e:
        print(str(e))


def set_token_email_change(mysql, uid, token, new_email):
    """
    Setze Token für E-Mailänderung.
    """
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y-%m-%d %H:%M:%S')
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_token_email_change", (uid, token, timestamp,
                                                   "change_email",
                                                   new_email,))
        mysql.commit()

    except Exception as e:
        print(str(e))


def get_reset_token_cp(mysql, uid, action, mode=None, app=None):
    """
    Setze Token für Passwortänderung.
    """
    cursor = mysql.cursor()
    try:
        cursor.callproc("get_reset_token_cp", (uid, action,))
        data = cursor.fetchall()

        if cursor.rowcount == 0:
            cursor.close()
            return None

        # Gebe das neue Passwort zurück, das nun in die Users-Tabelle
        # geschrieben wird (spezieller Modus, um nicht zu viele einzelne
        # Funktionen zu haben)
        if mode == "get_data":
            return data[0][2]
        # Gebe das Token zur Überprüfung zurück (eigentlicher
        # Standardmodus)
        return data[0][1]

    except Exception as e:
        if not app is None:
            app.logger.debug("Fehler bei get_reset_token_cp:\n" + str(e))
        return None


def delete_cp_token(mysql, uid, action):
    """
    Lösche Token für Controlpanel Aktionen.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("delete_cp_token", (uid, action,))
        mysql.commit()
        return 1, None
    except Exception as e:
        return -1, e


def set_email_for_user(mysql, uid, new_email, app):
    """
    Setze neue E-Mail für Benutzer.
    """
    cursor = mysql.cursor()

    try:
        cursor.callproc("set_email_for_user", (new_email, uid,))
        mysql.commit()
        return 1

    except Exception as e:
        app.logger.debug("Fehler bei set_email_for_user:\n" + str(e))
        return -1


def refresh_session_state(mysql, uid):
    """
    Refreshe die Session für den Benutzer.
    """
    cursor = mysql.cursor()
    session_start = datetime.datetime.now()
    session_max_alive = session_start \
                        + datetime.timedelta(minutes=__MAX_SESSION_TIME)

    try:
        cursor.callproc("refresh_session_state", (session_start,
                                                  session_max_alive, uid,))
        mysql.commit()
        return 1

    except Exception as e:
        return -1


def check_user_locked(mysql, uid):
    cursor = mysql.cursor()

    try:
        cursor.callproc("check_user_locked", (uid,))
        data = cursor.fetchall()

        if len(data) > 0 and data[0][1] >= 3:
            return -1
        else:
            return 0

    except Exception as e:
        return -2


def set_locked_count(mysql, uid):
    cursor = mysql.cursor()

    try:
        cursor.callproc("check_user_locked", (uid,))
        userexists = cursor.rowcount

        if userexists == 0:
            cursor.callproc("create_entry_user_locked", (uid,))

        if userexists == 1:
            cursor.callproc("iter_locked_counter", (uid,))

        mysql.commit()
        return 0

    except Exception as e:
        return -1


def search_for_query(mysql, query):
    cursor = mysql.cursor()
    cursor.callproc("tralala.get_all_posts")
    data = cursor.fetchall()

    if cursor.rowcount == 0:
        return None

    matches = []
    for record in data:
        hashtags = [x.lower() for x in str(record[4]).split(",")]

        if query in hashtags:
            matches.append([record[0],
                            record[1],
                            record[2],
                            record[3],
                            "#" + " #".join(hashtags),
                            record[5],
                            record[6]])

    return matches
