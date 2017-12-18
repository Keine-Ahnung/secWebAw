import json
import random
import time

from flask import Flask, request, session, url_for, redirect, render_template
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from tralala_logger import Logger

import function_helper
import security_helper
from db_handler import DB_Handler
from function_helper import generate_verification_token
import datetime

app = Flask(__name__)

app.config["MYSQL_DATABASE_USER"] = "db_admin_tralala"
app.config["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
app.config["MYSQL_DATABASE_DB"] = "tralala"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

mysql = MySQL()
mysql.init_app(app)  # Setup MySQL
logger = Logger("log")  # Setup eigener Logger

"""
    Sessionvariablen hier übersichtlich ordnen
"""
SESSIONV_LOGGED_IN = "logged_in"
SESSIONV_USER = "user"
SESSIONV_UID = "uid"
SESSIONV_ROLE_ID = "role_id"
SESSIONV_VERIFIED = "verified"
SESSIONV_ADMIN = "is_admin"

SESSIONV_ITER = [SESSIONV_LOGGED_IN, SESSIONV_USER, SESSIONV_UID, SESSIONV_ROLE_ID, SESSIONV_VERIFIED]

SESSIONID_ROLE_ADMIN = 5

"""
    Andere Konstanten
"""

DBC_CP_GETDATA = "get_data"


@app.route("/")
def index():
    """
    Startseite
    Hier muss ebenfalls die Darstellung aller Posts aus der DB behandelt werden
    """

    db_handler = DB_Handler()
    (code, data) = db_handler.get_all_posts(mysql)

    if code == -1:
        logger.debug("Keine Posts gefunden")
        return render_template("index.html", error_message="Keine Posts gefunden!")

    colors = ["red", "blue", "green", "yellow"]

    post_list = []

    for row in data:
        color_key = random.randint(0, 3)
        upvotes = int(row[5])
        downvotes = -int(row[6])  # Vorzeichenwechsel
        total_votes = upvotes + downvotes

        hashtags = ''
        for hashtag in row[4].split(','):
            hashtags = hashtags + '#' + hashtag + ' '  # space at the end

        html_trans = ""
        html_trans += "<div class=\"" + colors[color_key] + "\">"
        html_trans += "<div id=\"usr\">" + str(row[1]) + " | " + str(
            row[2]) + " | <b>Votes: " + str(total_votes) + "</b>"
        html_trans += "&nbsp;&nbsp;&nbsp;<a style=\"font-size: 150%; color: black;\" href=\"" + url_for(
            "vote") + "?method=upvote&post_id=" + str(
            row[0]) + "\">+</a>&nbsp;&nbsp;&nbsp;"
        html_trans += "<a style=\"font-size: 150%; color: black;\" href=\"" + url_for(
            "vote") + "?method=downvote&post_id=" + str(
            row[0]) + "\">-</a>&nbsp;&nbsp;&nbsp;</div>"
        html_trans += "</div>"
        html_trans += "</br>"
        html_trans += "<p>" + row[3] + "<p>"
        html_trans += "</br></br>"
        html_trans += "<div><b>" + hashtags + "</b>&nbsp;&nbsp;&nbsp;"
        html_trans += "</div>"
        post_list.append(html_trans)

    return render_template("index.html", post_list=post_list)


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    tbd
    """
    # Falls bereits eingeloggt
    try:
        session["logged_in"]
        return render_template("Du bist bereits eingeloggt!")
    except:
        pass

    # Hole Daten aus Loginform
    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"
        logger.error("Unzulässiger Zugriff mit HTTP-GET. Präsentiere JSON")
        return prepare_info_json(url_for("post_user"), "GET ist unzulaessig fUer den Login", return_info)

    login_email = request.form["login_email"]
    login_password = request.form["login_password"]

    if login_email == "" or login_password == "":
        return prepare_info_json(url_for("post_user"), "Es wurden Felder beim Login leergelassen")

    # Hashe Passwort
    login_password_hashed = generate_password_hash(login_password)

    # Suche nach User in DB
    db_handler = DB_Handler()
    (code, data) = db_handler.check_for_existence(mysql, login_email)
    if code == -1:
        logger.error("Gescheiterter Login (Datenbankfehler): " + login_email)
        return render_template("quick_info.html", info_danger=True,
                               info_text="Benutzername und/oder Passwort sind inkorrekt!")
    elif code == -2:
        logger.error("Gescheiterter Login (unbestätigt): " + login_email)
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst deinen Account bestätigen, bevor du dich einloggen kannst.")

    # Ueberprüfe gehashte Passwoerter
    if not check_password_hash(data["password"], login_password):
        logger.error("Gescheiterter Login (Übereinstimmung): " + login_email)
        return render_template("quick_info.html", info_danger=True,
                               info_text="Benutzername und/oder Passwort sind inkorrekt!")

    else:
        # Setze Sessionvariable
        session[SESSIONV_LOGGED_IN] = True
        session[SESSIONV_USER] = login_email
        session[SESSIONV_UID] = data["uid"]
        session[SESSIONV_ROLE_ID] = data["role_id"]
        if data["verified"] == 1:
            session[SESSIONV_VERIFIED] = True
        else:
            session[SESSIONV_VERIFIED] = False

        if data["role_id"] == SESSIONID_ROLE_ADMIN:
            session[SESSIONV_ADMIN] = True
        else:
            session[SESSIONV_ADMIN] = False
        # Starte Timeout Timer
        db_handler.start_session(mysql, data["uid"])
        logger.success("Erfolgreicher Login: " + login_email + " (ADMINISTRATOR)" if session[SESSIONV_ADMIN] else "")
        return render_template("quick_info.html", info_success=True,
                               info_text="Du wurdest eingeloggt. Willkommen zurück, " + login_email)


@app.route("/auth/logout", methods=["POST", "GET"])
@app.route("/logout", methods=["POST", "GET"])
def logout():
    """
    tbd
    """
    try:
        # Zugriff auf die Session Variable wirft einen KeyError. Durch den Catch wird das Template gerendert
        session["logged_in"]
    except:
        return render_template("quick_info.html", info_warning=True, info_text="Du bist nicht eingeloggt!")

    db_handler = DB_Handler()
    db_handler.invalidate_session(mysql, session["uid"])
    email = session[SESSIONV_USER]

    for sessionv in SESSIONV_ITER:
        session.pop(sessionv, None)
    logger.success("Benutzer wurde ausgeloggt: " + email)
    return render_template("quick_info.html", info_success=True, info_text="Du wurdest erfolgreich ausgeloggt!")


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
    """
    Ueberprüfe die Eingaben des Benutzers unabhaengig von der clientseitigen UeberprUefung.
    Sollten alle Eingaben korrekt sein, persistiere das neue Benutzerkonto in der Datenbank und schicke
    eine Bestaetigungsemail an die angegebene Email.
    :return:
    """
    try:
        session["logged_in"]  # Falls der User bereits eingeloggt ist, soll er auf die Startseite weitergeleitet werden
        return redirect(url_for("index"))
    except:
        pass

    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"

        logger.error("Unzulässiger Zugriff mit HTTP-GET. Präsentiere JSON")
        return prepare_info_json(url_for("post_user"), "GET ist unzulaessig für die Registration", return_info)

    else:
        reg_email = request.form["reg_email"]
        reg_password = request.form["reg_password"]
        reg_password_repeat = request.form["reg_password_repeat"]

        if reg_email == "" or reg_password == "" or reg_password_repeat == "":  # Reicht es, das allein durch JavaScript zu UeberprUefen?
            return prepare_info_json(url_for("post_user"), "Es wurden Felder bei der Registrierung leer gelassen")

        # Hier UeberprUefen und ggf. sanitizen

        if not security_helper.check_mail(reg_email):
            return render_template("registration_no_success.html", info_danger=True, code=5)

        # UeberprUefe, ob Password und Passwordwiederholung übereinstimmen
        if not reg_password == reg_password_repeat:
            return render_template("registration_no_success.html", info_danger=True, code=2)

        passed, comment = security_helper.check_password_strength(reg_password)
        if not passed:
            return render_template("registration_no_success.html", info_danger=True, code=4, comment=comment)

        # Ueberprüfe, ob User schon existiert
        success = register_new_account(mysql, reg_email, generate_password_hash(reg_password),
                                       generate_verification_token(50))
        if success == -1:
            logger.error("Benuzter konnte nicht in Datenbank geschrieben werden.")
            return render_template("registration_no_success.html", info_danger=True, code=-1)
        elif success == 0:
            logger.error("Fehler bei Registrierung. Benutzer existiert bereits.")
            return render_template("registration_no_success.html", info_danger=True, code=0, reg_email=reg_email)

        success = send_verification_email(reg_email)

        if success == -1:
            logger.error("Fehler beim Senden der Bestätigungsmail an: " + reg_email)
            return render_template("registration_no_success.html", info_danger=True, code=3, reg_email=reg_email)

        logger.success("Registrierung war erfolgreich für Benutzer: " + reg_email + ". Sende Bestätigungsmail...")
        return render_template("registration_success.html", reg_email=reg_email)


@app.route("/auth/admin/dashboard")
@app.route("/auth/dashboard")
def admin_dashboard():
    """
    tbd
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        logger.error("Unbefugter Benutzer '" + session[
            SESSIONV_USER] + " versucht auf das Admin Dashboard zuzugreifen. Verweigere Zugriff.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt und Administrator sein, um diese Aktion durchführen zu dürfen")

    if not session[SESSIONV_ADMIN]:
        logger.error("Unbefugter Benutzer '" + session[
            SESSIONV_USER] + " versucht auf das Admin Dashboard zuzugreifen. Verweigere Zugriff.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    # Benutzerdaten holen
    db_handler = DB_Handler()
    (code_users, users) = db_handler.get_all_users(mysql)
    (code_roles, roles) = db_handler.get_all_roles(mysql)

    if code_users == -1 or code_roles == -1:
        logger.error("Fehler beim Laden des Admin Dashboards...")
        return render_template("admin.html",
                               error="Admin Dashboard konnte nicht geladen werden. Versuche es später noch einmal.")

    # In Dashboard eintragen
    logger.success("Administrator '" + session[SESSIONV_USER] + " hat Admin Dashboard geladen")
    return render_template("admin.html", admin_active="active", users=users, roles=roles)


@app.route("/confirm")
def confirm():
    """
    tbd
    """
    # Suche nach Email basierend auf Token
    token = request.args.get("token")

    db_handler = DB_Handler()
    (success, email) = db_handler.get_user_for_token(mysql, token)
    if success == -1:
        logger.error("Unbekanntes Token wurde übergeben")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der Benutzer konnte nicht bestaetigt werden!")

    if success == 2:
        logger.success("Benutzer '" + email + "' wurde bereits bestätigt")
        return render_template("quick_info.html", info_warning=True, info_text="Der Benutzer wurde bereits bestaetigt!")

    # Setze Token auf Defaultwert und setze verified auf 1
    success = db_handler.user_successful_verify(mysql, email)

    if success == -1:
        logger.error("Benutzer '" + email + "' konnte nicht bestätigt werden (Datenbankfehler)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der Benutzer konnte nicht bestätigt werden!")

    if success == 1:
        logger.success("Benutzer " + email + " wurde bestätigt")
        return render_template("quick_info.html", info_success=True,
                               info_text="Der Benutzer wurde erfolgreich bestaetigt. Du kannst dich nun einloggen.")


@app.route("/auth/write_post")
def write_post():
    return render_template("new_post.html", new_post_active="active")


@app.route("/auth/post_message", methods=["POST", "GET"])
def post_message():
    try:
        session["logged_in"]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um eine Nachricht zu posten!")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Post sanitizen
    message = request.form["post_message"]
    hashtags = request.form["post_hashtags"]

    if message == "":
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnte deine Nachricht nicht gepostet werden, da du keine Nachricht"
                                         " angegeben hast. Versuche es bitte erneut!")

    # Nur bestätigte Benutzer dürfen voten
    if not session["verified"]:
        logger.error(
            "Benutzer " + session[SESSIONV_USER] + " wollte Nachricht posten, ohne den Account bestätigt zu haben")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst deinen Account zuerst bestätigen, bevor du etwas posten kannst.")

    # Post in DB schreiben
    success = db_handler.post_message_to_db(mysql, session["uid"], None, message[:279], hashtags)

    if success == -1:
        logger.error("Post von Benutzer " + session[SESSIONV_USER] + " (" + message[
                                                                            :50] + "...)" + " konnte nicht gepostet werden (Datenbankfehler)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Nachricht konnte nicht geposted werden. Versuche es erneut!")
    elif success == 1:
        logger.success("Neue Nachricht von Benuzter " + session[SESSIONV_USER] + " geposted")
        return render_template("quick_info.html", info_success=True,
                               info_text="Deine Nachricht wurde geposted. Du kannst sie auf der Postseite nun sehen!")

    return "post message uid=" + str(session["uid"]) + " message=" + message + " hashtags=" + hashtags


@app.route("/auth/vote")
def vote():
    """

    /vote_up?method=...&post_id=123
    """
    db_handler = DB_Handler()

    try:
        session["logged_in"]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True, info_text="Du musst eingeloggt sein, um zu voten!")

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("session_timeout.html",
                                   timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Lese GET-Parameter
    method = request.args.get("method")
    post_id = request.args.get("post_id")
    uid = session["uid"]

    if post_id == "" or method == "":
        logger.error("Ungültiger Zugriff (Post ID oder Methode)")
        return render_template("quick_info.html", info_danger=True, info_text="Ungültige Post ID oder Zugriffsmethode!")

    (code, data) = db_handler.check_if_already_voted(mysql, post_id, uid)

    if code == -1:
        logger.success("Benutzer " + session[SESSIONV_USER] + " hat bereits für Post " + str(post_id) + " abgestimmt")
        return render_template("quick_info.html", info_warning=True,
                               info_text="Du hast bereits für diesen Post gevoted.")

    # Hole Post aus DB
    (code, data) = db_handler.get_post_by_pid(mysql, post_id)

    if code == -1:
        logger.error("Fehlerhafter Link für Vote. Möglicherweise wurde dieser manipuliert.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keinen Post mit der ID " + str(post_id) + " finden!")

    method_labels = {"upvote": "Upvote", "downvote": "Downvote"}
    csrf_seq = generate_verification_token(8)

    # Gebe Seite mit vollstaendigem Post zurück
    # Praesentiere zufaellige Zeichenfolge, die eingegeben werden muss, um CSRF-Attacken zu unterbinden
    logger.success("Gebe Seite mit CSRF Token zurück. Warte auf Eingabe von Benutzer...")
    return render_template("vote.html", post=data, csrf_seq=csrf_seq, method=method,
                           method_label=method_labels[method])


@app.route("/auth/finish_vote", methods=["GET", "POST"])
def finish_vote():
    """
    tbd
    """
    # Hole GET-Parameter
    csrf_token = request.args.get("csrf_token")
    post_id = request.args.get("post_id")
    method = request.args.get("method")
    input_csrf = request.form["vote_code"]
    uid = session["uid"]

    try:
        post_id_int = int(post_id)
    except:
        logger.error("Post ID konnte nicht zu INT umgewandelt werden. Möglicher Versuch einer SQL Injection erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")

    if input_csrf == "" or csrf_token == "" or post_id == "" or post_id_int < 0 or not method in ["upvote", "downvote"]:
        logger.error(
            "Request um den Vote abzuschließen wies ungültige Parameter(formen) auf. Vote kann nicht abgeschlossen werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")
    # Ueberprüfe csrf_seq
    if not csrf_token == input_csrf:
        logger.error("Vote konnte nicht abgeschlossen werden (keine Übereinstimmung der Token)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der eingegebene Code war leider falsch. Bitte versuche es erneut!")

    # Persistiere Vote
    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    (code, data) = db_handler.check_if_already_voted(mysql, post_id, uid)

    if code == -1:
        logger.error("Benutzer " + session[SESSIONV_USER] + " hat bereits für den Post abgestimmt.")
        return render_template("quick_info.html", info_warning=True,
                               info_text="Du hast bereits für diesen Post gevoted.")

    if method == "upvote":
        # Registriere Upvote
        success_register = db_handler.register_vote(mysql, post_id, uid, "upvote")

        # Poste Upvote
        success = db_handler.do_upvote(mysql, post_id)
        if success == -1 or success_register == -1:
            logger.error("Fehler beim Persistieren des Upvotes (Datenbankfehler)")
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Etwas ist schiefgelaufen! Versuche es erneut!")
        logger.success("Upvote für " + str(post_id) + " von " + session[SESSIONV_USER] + " wurde registriert.")
        return render_template("quick_info.html", info_success=True, info_text="Upvote erfolgreich!")

    elif method == "downvote":
        # Registriere Downvote
        success_register = db_handler.register_vote(mysql, post_id, uid, "downvote")

        # Poste Downvote
        success = db_handler.do_downvote(mysql, post_id)
        if success == -1 or success_register == -1:
            logger.error("Fehler beim Persistieren des Downvotes (Datenbankfehler)")
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Etwas ist schiefgelaufen! Versuche es erneut!")
        logger.success("Downvote für " + str(post_id) + " von " + session[SESSIONV_USER] + " wurde registriert.")
        return render_template("quick_info.html", info_success=True, info_text="Downvote erfolgreich!")


@app.route("/auth/controlpanel/change-email")
def change_email():
    """
    tbd
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    return render_template("email_change.html")


@app.route("/auth/controlpanel/change_email_handler", methods=["POST"])
def change_email_handler():
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    new_email = request.form["new_email"]
    new_email_confirm = request.form["new_email_confirm"]
    confirm_pass = request.form["confirm_pass"]

    if not function_helper.check_params("password", confirm_pass) or not function_helper.check_params("email",
                                                                                                      new_email) or not function_helper.check_params(
        "email", new_email_confirm):
        logger.error("Eingegebene E-Mail oder Passwort entsprach nicht den vorgegebenen Richtlinien.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Bitte fülle alle Felder aus und beachte die Passwortrichtlinien.")

    if not new_email == new_email_confirm:
        logger.error("Eingegebene E-Mail weicht von der Session E-Mail ab.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Die Bestätigung der neuen E-Mail stimmt nicht mit der neuen Mail überein. Bitte versuche es erneut.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    user_email = session[SESSIONV_USER]
    curr_pass = db_handler.get_password_for_user(mysql, user_email)[
        1]  # Greife auf Index 1 zu, da Tupel zurückgegeben wird mit (1, "pbkdf2:sha256:xxx")
    uid = int(session[SESSIONV_UID])

    # Überprüfe, ob das eingegebene Passwort richtig war

    if not check_password_hash(curr_pass, confirm_pass):
        logger.error("Das eingegebene Passwort für Benutzer " + session[SESSIONV_USER] + " war falsch.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das eingegebene Passwort war falsch. Bitte versuche es erneut.")

    # Confirm Token in Datenbank festschreiben
    token = generate_verification_token(32)
    db_handler.set_token_email_change(mysql, uid, token, new_email)

    # Bestätigungsmail senden
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y-%m-%d %H:%M:%S')

    function_helper.send_mail_basic(user_email,
                                    "Änderung der E-Mail",
                                    "Hallo " + user_email + ",\n bitte klicke auf den folgenden Link, um die Änderung deiner E-Mail um " + str(
                                        timestamp) + " zu bestätigen.\n\nlocalhost:5000" + url_for(
                                        "confirm_email_change") + "?uid=" + str(uid) + "&token=" + str(token))
    logger.success("Bestätigungsmail für E-Mail Änderung wurde an " + user_email + " gesendet.")
    return render_template("quick_info.html", info_success=True,
                           info_text="Wir haben eine Bestätigungsmail an die angegebene E-Mail Adresse geschickt. Der darin enthaltene Link bestätigt deine Änderung.")


@app.route("/auth/controlpanel/confirm_email_change")
def confirm_email_change():
    uid = request.args.get("uid")
    token = request.args.get("token")

    if not function_helper.check_params("id", uid) or not function_helper.check_params("text", token):
        logger.error("URL-Parameter konnten nicht verarbeitet werden (ungültiges Format).")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine übermittelte Anfrage nicht verstehen. Bitte verändere nichts an dem Link, den wir dir geschickt haben.")

    try:
        int(uid)
    except:
        logger.error("Die UID des Bestätigungslinks kann nicht in INT umgewandelt werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine übermittelte Anfrage nicht verstehen. Bitte verändere nichts an dem Link, den wir dir geschickt haben.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    sys_token = db_handler.get_reset_token_cp(mysql, int(uid), "change_email", app=app)

    if sys_token == None:
        logger.error("Keine Änderungsanfrage für die E-Mail für UID " + str(uid) + " gefunden (sys_token is None)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keine zugehörige Anfrage zur Passwortänderung im System finden. Bitte achte darauf, nichts an dem Link zu verändern und versuche es erneut.")

    if not sys_token == token:
        logger.error("Das über die URL übergebene Token stimmt nicht mit dem im System registrierten Token überein.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das übermittelte Token war ungültig.")

    new_email = db_handler.get_reset_token_cp(mysql, int(uid), "change_email", mode=DBC_CP_GETDATA)

    db_handler.set_email_for_user(mysql, int(uid), new_email, app)

    # Tabelle aufräumen
    db_handler.delete_cp_token(mysql, int(uid), "change_email")
    logger.success(
        "Benutzer " + str(uid) + " hat seine E-Mail geändert. Räume Tabelle mit alten Einträgen dieses Users auf...")

    delete_user_session()
    logger.debug("Logge User aus, um sich mit den neuen Credentials anzumelden.")

    return render_template("quick_info.html", info_success=True, info_text="Die E-Mail wurde geändert.")


@app.route("/auth/controlpanel/change_password")
def change_password():
    """
    tbd
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    return render_template("password_change.html")


@app.route("/auth/controlpanel/change_password_handler", methods=["POST"])
def change_password_handler():
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    old_pass = request.form["old_password"]
    new_pass = request.form["new_password"]
    new_pass_confirm = request.form["new_password_confirm"]

    if not function_helper.check_params("password", old_pass) or not function_helper.check_params("password",
                                                                                                  new_pass) or not function_helper.check_params(
        "password", new_pass_confirm):
        logger.error("Eingegebene E-Mail oder Passwort entsprach nicht den vorgegebenen Richtlinien.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Bitte fülle alle Felder aus und beachte die Passwortrichtlinien.")

    if not new_pass == new_pass_confirm:
        logger.error("Passwörter stimmen nicht überein (Bestätigung).")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Die Bestätigung des neuen Passworts stimmt nicht mit dem neuen Passwort überein. Bitte versuche es erneut.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    user_email = session[SESSIONV_USER]
    curr_pass = db_handler.get_password_for_user(mysql, user_email)[
        1]  # Greife auf Index 1 zu, da Tupel zurückgegeben wird mit (1, "pbkdf2:sha256:xxx")
    uid = int(session[SESSIONV_UID])

    if not check_password_hash(curr_pass, old_pass):
        logger.error("Das eingegebene Passwort für Benutzer " + session[SESSIONV_USER] + " war falsch.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das eingegebene Passwort war falsch. Bitte versuche es erneut.")

    # Confirm Token in Datenbank festschreiben
    token = generate_verification_token(32)
    db_handler.set_token_password_change(mysql, uid, token, generate_password_hash(new_pass))

    # Bestätigungsmail senden
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y-%m-%d %H:%M:%S')

    function_helper.send_mail_basic(user_email,
                                    "Änderung des Passworts",
                                    "Hallo " + user_email + ",\n bitte klicke auf den folgenden Link, um die Änderung deines Passworts um " + str(
                                        timestamp) + " zu bestätigen.\n\nlocalhost:5000" + url_for(
                                        "confirm_password_change") + "?uid=" + str(uid) + "&token=" + str(token))

    logger.success("Bestätigungsmail für Passwortänderung wurde an " + user_email + " gesendet.")

    return render_template("quick_info.html", info_success=True,
                           info_text="Wir haben eine Bestätigungsmail an die angegebene E-Mail Adresse geschickt. Der darin enthaltene Link bestätigt deine Änderung.")


@app.route("/auth/controlpanel/confirm_password_change")
def confirm_password_change():
    uid = request.args.get("uid")
    token = request.args.get("token")

    if not function_helper.check_params("id", uid) or not function_helper.check_params("text", token):
        logger.error("URL-Parameter konnten nicht verarbeitet werden (ungültiges Format).")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine übermittelte Anfrage nicht verstehen. Bitte verändere nichts an dem Link, den wir dir geschickt haben.")

    try:
        int(uid)
    except:
        logger.error("Die UID des Bestätigungslinks kann nicht in INT umgewandelt werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine übermittelte Anfrage nicht verstehen. Bitte verändere nichts an dem Link, den wir dir geschickt haben.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    sys_token = db_handler.get_reset_token_cp(mysql, int(uid), "change_password", app=app)

    if sys_token == None:
        logger.error("Keine Änderungsanfrage für die E-Mail für UID " + str(uid) + " gefunden (sys_token is None)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keine zugehörige Anfrage zur Passwortänderung im System finden. Bitte achte darauf, nichts an dem Link zu verändern und versuche es erneut.")

    if not sys_token == token:
        logger.error("Das über die URL übergebene Token stimmt nicht mit dem im System registrierten Token überein.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das übermittelte Token war ungültig.")

    new_pass = db_handler.get_reset_token_cp(mysql, int(uid), "change_password", mode=DBC_CP_GETDATA)

    db_handler.set_pass_for_user(mysql, int(uid), new_pass, app)

    # Tabelle aufräumen
    db_handler.delete_cp_token(mysql, int(uid), "change_password")
    logger.success(
        "Benutzer " + str(uid) + " hat Passwort geändert. Räume Tabelle mit alten Einträgen dieses Users auf...")

    delete_user_session()
    logger.debug("Logge User aus, um sich mit den neuen Credentials anzumelden.")

    return render_template("quick_info.html", info_success=True, info_text="Das Passwort wurde geändert.")


@app.route("/reset_password1", methods=["GET", "POST"])
def reset_password1():
    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"

        return prepare_info_json(url_for("post_user"),
                                 "GET ist unzulaessig fUer den Login",
                                 return_info)
    elif request.method == "POST":
        reset_email = request.form["reset_email"]

        if reset_email is not None or not reset_email == "":
            function_helper.reset_password(mysql=mysql, mail=reset_email,
                                           url=url_for('/reset_password/action'))


@app.route("/auth/admin/delete_user", methods=["POST", "GET"])
def delete_user():
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator und eingeloggt sein, um diese Aktion durchführen zu dürfen")

    if not session[SESSIONV_ADMIN]:
        logger.error(
            "Unbefugter Benutzer " + session[SESSIONV_USER] + " wollte User löschen. Mögliche Attacke erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    uid = request.args.get("uid")
    password = request.form["password"]

    try:
        int(uid)
    except:
        logger.error("Kann die UID nicht zu INT umwandeln.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="User ID muss ein INT sein.")

    if not password:
        logger.error("Bestätigung schlug fehl (Passwort fehlt).")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Bitte gebe ein Passwort ein.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return render_template("quick_info.html", info_warning=True,
                                   info_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Überprüfe, ob Passwork korrekt
    (code, data) = db_handler.get_password_for_user(mysql, session[SESSIONV_USER])

    if code == -1:
        logger.error("Konnte Benutzerdaten für Administrator nicht abrufen (Datenbankfehler)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Konnte Benutzerdaten nicht abrufen. Bitte versuche es erneut.")

    if not check_password_hash(data, password):
        logger.error("Eingegebenes Passwort des Administrators war falsch.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das eingegebene Passwort war ungültig.")

    (code, e) = db_handler.delete_user(mysql, int(uid))

    if code == -1:
        logger.error("Benutzer " + str(uid) + " konnte nicht gelöscht werden (Datenbankfehler). Stacktrace: " + str(e))
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ein unerwarteter Fehler ist aufgetreten.")
    elif code == 1:
        logger.success("Benutzer " + str(uid) + " wurde gelöscht.")
        return render_template("quick_info.html", info_success=True,
                               info_text="Benutzer (UID: " + str(uid) + ") wurde gelöscht.")
    else:
        logger.error("Unerwarteter Fehler beim Löschen des Benutzers " + str(uid))
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ein unerwarteter Fehler ist aufgetreten.")


@app.route("/auth/admin/confirm")
def admin_confirm():
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator und eingeloggt sein, um diese Aktion durchführen zu dürfen")

    if not session[SESSIONV_ADMIN]:
        logger.error("Unebfugter Benutzer " + session[
            SESSIONV_USER] + " möchte auf eine Adminfunktion zugreifen. Mögliche Attacke erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    method = request.args.get("method")
    obj = request.args.get("obj")

    try:
        int(obj)
    except:
        logger.error("obj konnte nicht zu INT umgewandelt werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Objekt muss ein INT sein.")

    if not method in ["delete"]:
        logger.error("Unbekannte Methode. Erlaubt sind: delete")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ungültige Aktion. Bitte versuche es erneut.")

    logger.success(
        "Adminstratorfunktion wurde erfolgreich bestätigt. (Methode:" + str(method) + ", Objekt: " + str(obj))
    return render_template("confirm_admin.html", obj=obj, method=method)


@app.route("/reset/password")
def reset_password():
    return render_template("reset_password.html")


@app.route("/reset/password/handle", methods=["POST"])
def handle_password_reset():
    try:
        if session[SESSIONV_LOGGED_IN]:  # Nur eingeloggte Benutzer dürfen Nachrichten posten
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Du bist bereits eingeloggt. Du musst dich zuerst ausloggen, bevor du dein Passwort zurücksetzen kannst.")
    except:
        pass

    email = request.form["reset_email"]

    if not function_helper.check_params("email", email):
        logger.error("E-Mail besitzt ein ungültiges Format")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Die E-Mail besitzt ein ungültiges Format. Bitte versuche es erneut.")

    db_handler = DB_Handler()

    # Überprüfe, ob Account mit angegebener E-Mail existiert
    (code, data) = db_handler.check_for_existence(mysql, email)
    if code != 1:
        logger.error("Konnte keinen Benutzer mit der E-Mail " + str(email) + " finden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keinen Account mit der angegebenen E-Mail finden. Bitte Überprüfe die E-Mail und versuche es erneut.")

    uid = data["uid"]

    # Überprüfe auf Spam Attacke bzw. zu viele Passwort Resets
    if not db_handler.count_password_requests(mysql, int(uid), app):
        logger.error("Für Benutzer " + str(
            uid) + " wurde mehr als 5 mal versucht, das Passwort zurückzusetzen. Mögliche Spam-Attacke erkannt. Timout für Benutzer " + str(
            uid))
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du hast zu oft versucht dein Passwort zurückzusetzen, weshalb wir dieses Feature für dich vorübergehend deaktiviert haben, um mögliche Spam-Attacken zu verhindern. Vielen Dank für dein Verständnis.")

    # Persistiere Reset Token
    token = function_helper.generate_verification_token(32)
    db_handler.set_reset_token(mysql, token, uid, app)

    # Sende Reset Email
    function_helper.send_reset_mail(email, uid, token, url_for("confirm_password_reset"), app)

    logger.success("Anfrage für Passwort Reset wurde registriert. Sende Reset E-Mail an " + email)

    return render_template("quick_info.html", info_success=True,
                           info_text="Falls deine E-Mail Adresse bei uns registriert ist, haben wir dir eine E-Mail mit weiteren Anweisungen zum Vorgehen geschickt.")


@app.route("/reset/password/confirm_reset")
def confirm_password_reset():
    """
    Handler, um den Passwort Reset Link auszuwerten und anschließend auf die Seite weiterzuleiten, auf der das neue Passwort gesetzt
    werden kann
    :return:
    """
    try:
        if session[SESSIONV_LOGGED_IN]:  # Nur eingeloggte Benutzer dürfen Nachrichten posten
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Du bist bereits eingeloggt. Du musst dich zuerst ausloggen, bevor du den Password Reset vervollständigen kannst.")
    except:
        pass

    token = request.args.get("token")
    uid = request.args.get("uid")

    if not function_helper.check_params("text", token) or not function_helper.check_params("id", uid):
        logger.error("Konnte die übergebenen URL-Parameter nicht auswerten.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine Anfrage nicht verstehen. Bitte ändere nichts an dem Link, den wir dir per Mail zugeschickt haben.")

    db_handler = DB_Handler()
    ref_token = db_handler.get_reset_token(mysql, uid)

    if ref_token is None:
        logger.error("Kein zugehöriger Passwort Reset Request für Token " + str(ref_token) + " gefunden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Es wurde kein zugehöriger Passwort Request in unserem System gefunden. Bitte versuche es erneut.")

    if not token == ref_token:
        logger.error(
            "Übermitteltes Token stimmt nicht mit registriertem Token überein. Mögliche Attacke (SQLi) erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Token stimmen nicht überein.")
    return render_template("password_reset_change.html", token=ref_token, uid=uid)


@app.route("/reset/password/set_new", methods=["POST"])
def set_new_password():
    try:
        if session[SESSIONV_LOGGED_IN]:  # Nur eingeloggte Benutzer dürfen Nachrichten posten
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Du bist bereits eingeloggt. Du musst dich zuerst ausloggen, bevor du den Password Reset vervollständigen kannst.")
    except:
        pass

    new_pass = request.form["new_password"]
    new_pass_confirm = request.form["new_password_confirm"]
    hidden_token = request.form["h_token"]
    hidden_uid = request.form["h_uid"]

    # Überprüfe auf korrekte Form der Parameterinhalte
    if not function_helper.check_params("password", new_pass) or not function_helper.check_params("password",
                                                                                                  new_pass_confirm) or not function_helper.check_params(
        "text", hidden_token) or not function_helper.check_params("id", hidden_uid):
        logger.error("Übergebene URL-Parameter entsprechen nicht dem erwarteten Format.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten deine Anfrage leider nicht verarbeiten, da einige Felder entweder leer waren oder das falsche Format aufwiesen")

    # Überprüfe auf Gleichheit der Passwörter
    if not new_pass == new_pass_confirm:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Die beiden Passwörter stimmen leider nicht überein. Bitte versuche es erneut.")

    # Überprüfe, ob Token und ID korrekt sind und setze anschließend das Passwort
    db_handler = DB_Handler()

    ref_token = db_handler.get_reset_token(mysql, int(hidden_uid))

    if not ref_token == hidden_token:
        logger.error("Das übermittelte Reset Token stimmt leider nicht mit dem registrierten Token überein.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das übermittelte Reset Token stimmt leider nicht mit dem uns bekannten Token überein. Es ist möglich, dass dieses während der Übertragung verändert wurde. Bitte versuche es erneut.")

    # Hole mit dem Token korrespondierendes Token aus der Datenbank
    (uid, token) = db_handler.get_reset_token(mysql, hidden_uid, "get_token_uid")

    # Schreibe neues Passwort in die Datenbank
    hashed_pass = generate_password_hash(new_pass)
    db_handler.set_pass_for_user(mysql, uid, hashed_pass, app)
    logger.success("Passwort für Benutzer " + str(uid) + " wurde geändert.")

    # Lösche Tokeneintrag aus der Datenbank
    db_handler.delete_pass_reset_token(mysql, uid, app)
    logger.debug("Logge Benutzer " + str(uid) + " aus, um sich mit den geänderten Credentials erneut auszuloggen.")

    return render_template("quick_info.html", info_success=True,
                           info_text="Dein Passwort wurde geändert. Du kannst dich nun einloggen.")


'''
Method receiving the token to perform the recheck and the password reset
'''


@app.route("/reset_password/action", methods=["GET", "POST"])
def reset_password_action():
    """
    Erhält Daten des neuen Passworts. Ändert Passwort des Benutzers in der Datenbank.
    Wichtig: Setze das Passwort nur für die User ID die für das Token aus der Datenbank ausgelesen wurde und nicht das Passwort der UID,
    die über die URL mitgegeben wurde!
    :return:
    """
    token = request.form["token"]
    uid = request.form["uid"]
    token_check = function_helper.compare_reset_token(mysql, uid, token)

    if token_check:
        return render_template()
    else:
        return render_template()


"""
Hilfsfunktionen, die keine HTTP Requests bearbeiten
"""


def delete_user_session():
    session.pop("logged_in", None)
    session.pop("user", None)
    session.pop("uid", None)
    session.pop("role_id", None)
    session.pop("verified", None)

    

def check_for_session_state(uid):
    db_handler = DB_Handler()

    (code, data) = db_handler.check_session_state(mysql, uid)

    if code == 1:
        app.logger.debug(data)
        return True

    if code == -1:
        app.logger.debug(data)
        return False


def send_verification_email(reg_email):
    """
        Sende Bestaetigungsmail mit Verification Token.
    """

    app.logger.debug("Sende Bestaetigungsmail.")

    # Hole Verification Token aus der DB
    db_handler = DB_Handler()
    (success, token) = db_handler.get_token_for_user(mysql, reg_email)

    if success == -1:
        return -1

    try:
        url = 'localhost:5000' + url_for('confirm') + '?token=' + token
        function_helper.send_verification_mail(reg_email, url)
    except Exception as e:
        app.logger.error("Fehler beim Senden der Bestaetigungsmail."
                         "..\n" + str(e))
        return -1

    app.logger.debug("Bestaetigungsemail gesendet an '" + reg_email + "' ...")
    return 1


def prepare_info_json(affected_url, info_text, additions):
    """
        Gebe eine Info- bzw. Fehlermeldung im JSON-Format zurUeck.
        Dictionary akzeptiert keine additions, falls folgende Keys in den
        additions existieren:
            1. called_url
            2. timestamp
            3. info_text
        Durch eine Exception wird der dict merge abgebrochen
    """

    return_info = {}
    return_info["info_text"] = info_text
    return_info["called_url"] = str(affected_url)
    return_info["timestamp"] = str(time.ctime())

    copy = return_info.copy()

    try:
        return_info.update(additions)
    except:
        return json.dumps(copy, indent=4)

    return json.dumps(return_info, indent=4)


def log_e(m):
    pass


"""
    Zugriff auf die DB mit der DB_Handler Klasse
"""


def register_new_account(mysql, email, pw_hash, verification_token):
    db_handler = DB_Handler()
    success = db_handler.add_new_user(mysql, email, pw_hash, verification_token)

    return success


if __name__ == '__main__':
    app.secret_key = "e5ac358c-f0bf-11e5-9e39-d3b532c10a28"  # Wichtig für Sessions, da Cookies durch diesen Key signiert sind!
    logger.debug("Server Reload...")
    app.run(debug=True)
