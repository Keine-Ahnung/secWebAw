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
from function_helper import generate_token
import datetime
import bleach

# Erstellung der App
app = Flask(__name__)

# MySQL Credentials
app.config["MYSQL_DATABASE_USER"] = "db_admin_tralala"
app.config["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
app.config["MYSQL_DATABASE_DB"] = "tralala"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

# Setup MySQL
mysql = MySQL()
mysql.init_app(app)

# Setup Logger
logger = Logger("log")  # Setup eigener Logger

# Sessionvariablen
SESSIONV_LOGGED_IN = "logged_in"
SESSIONV_USER = "user"
SESSIONV_UID = "uid"
SESSIONV_ROLE_ID = "role_id"
SESSIONV_VERIFIED = "verified"
SESSIONV_ADMIN = "is_admin"
SESSIONV_ITER = [SESSIONV_LOGGED_IN, SESSIONV_USER, SESSIONV_UID, SESSIONV_ROLE_ID,
                 SESSIONV_VERIFIED]  # Iterable, für Session Termination

# Muss von Hand geänder werden, sollte sich die Rollen-ID des Administrators ändern!
SESSIONID_ROLE_ADMIN = 5

# Funktionmodi
DBC_CP_GETDATA = "get_data"  # Modus für db_handler.get_reset_token_cp. Wird im DB_Handler verwendet um nur die Daten zurückzugeben, die zu einem Change Request gespeichert wurden (bspw. neue E-Mail oder neues Passwort)

"""
Flask Handler
####################################################
"""


@app.route("/")
@app.route("/index")
def index():
    """
    Landing Page der Webapplikation. Kann durch "/" oder "/index" aufgerufen werden.

    Die Indexseite der Webapplikation stellt zugleich die Übersicht der Posts dar.
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


@app.route("/login", methods=["POST"])
def login():
    """
    Ziel des Loginformulars. Überprüft in der Datenbank auf Existenz des angegebenen Benutzers als auch der Übereinstimmung
    des Passworts. Nur bestätigte Benutzer können sich einloggen.

    Bei erfolgreichem Login wird eine Session erstellt, die wichtige Werte speichert, die zur Identifikation auf weiteren Seiten
    benötigt wird:

    - logged_in: True, wenn eingeloggt.
    - user: Login-Email des angemeldeten Benutzeraccounts
    - uid: User-ID des Benutzers
    - role_id: Rollen-ID des Benutzers (3 unverified, 4 verified, 5 administrator)
    - is_admin: True, wenn die Rollen-ID des Benutzers 5 ist
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
        return prepare_info_json(url_for("post_user"), "GET ist unzulässig für den Login", return_info)

    login_email = request.form["login_email"]
    login_password = request.form["login_password"]

    # Hier soll lediglich auf die Länge der Credentials getestet werden. Ein Test auf Passwortstärke wäre unnötig, da dieser bereits bei der Registrierung durchgeführt wurde
    if not function_helper.check_params("text", login_email) or not function_helper.check_params("text",
                                                                                                 login_password):
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
        db_handler.start_session(mysql, data[
            "uid"])  # Trage neue Session in Session-Tabelle ein, um den automatischen Logout zu tracken
        logger.success("Erfolgreicher Login: " + login_email + (" (ADMINISTRATOR)" if session[SESSIONV_ADMIN] else ""))
        return render_template("quick_info.html", info_success=True,
                               info_text="Du wurdest eingeloggt. Willkommen zurück, " + login_email)


@app.route("/auth/logout")
@app.route("/logout")
def logout():
    """
    Logge den aktuell angemeldeten Benutzer aus => Terminiere die Session, indem die Session-Variablen aus der Session
    gepopped werden.

    Zusätzlich wird die aktuelle Session aus der Sessions-Tabelle gelöscht.
    """
    try:
        # Zugriff auf die Session Variable wirft einen KeyError. Durch den Catch wird das Template gerendert
        session["logged_in"]
    except:
        return render_template("quick_info.html", info_warning=True, info_text="Du bist nicht eingeloggt!")

    db_handler = DB_Handler()
    db_handler.invalidate_session(mysql, session["uid"])  # Lösche Session aus der Trackingtabelle
    email = session[SESSIONV_USER]

    for sessionv in SESSIONV_ITER:
        session.pop(sessionv, None)
    logger.success("Benutzer wurde ausgeloggt: " + email)
    return render_template("quick_info.html", info_success=True, info_text="Du wurdest erfolgreich ausgeloggt!")


@app.route("/signup/post_user", methods=["POST"])
def post_user():
    """
    Überprüfe die Eingaben des Benutzers unabhängig von der clientseitigen Überprüfung.
    Sollten alle Eingaben korrekt bzw. valide sein, persistiere das neue Benutzerkonto in der Datenbank und schicke
    eine Bestaetigungsemail an die angegebene Email.

    - Nach Registrierung und vor Bestätigung: Benutzer ist unverified => role_id = 3
    - Nach Registrierung und nach Bestätigung: Benutzer ist verified => role_id = 4
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

        if not function_helper.check_params("text", reg_email) or not function_helper.check_params("text",
                                                                                                   reg_password) or not function_helper.check_params(
            "text", reg_password_repeat):
            return prepare_info_json(url_for("post_user"),
                                     "Es wurden Felder bei der Registrierung leer gelassen")  # Gebe als JSON zurück, da per einfacher Registrierung durch Formular nicht erreichbar

        if not security_helper.check_mail(reg_email):
            return render_template("registration_no_success.html", info_danger=True, code=5)

        # Überprüfe, ob Passwort und Passwortwiederholung übereinstimmen
        if not reg_password == reg_password_repeat:
            return render_template("registration_no_success.html", info_danger=True, code=2)

        passed, comment = security_helper.check_password_strength(reg_password)
        if not passed:
            return render_template("registration_no_success.html", info_danger=True, code=4, comment=comment)

        # Überprüfe, ob User schon existiert
        success = register_new_account(mysql, reg_email, generate_password_hash(reg_password),
                                       generate_token(50))  # Persistiere neuen Benutzer in der Datenbank
        if success == -1:
            logger.error("Benuzter konnte nicht in Datenbank geschrieben werden.")
            return render_template("registration_no_success.html", info_danger=True, code=-1)
        elif success == 0:
            logger.error("Fehler bei Registrierung. Benutzer existiert bereits.")
            return render_template("registration_no_success.html", info_danger=True, code=0, reg_email=reg_email)

        success = send_verification_email(
            reg_email)  # Sende Mail mit Bestätigungslink an die angegebene E-Mail, mit dem die Registrierung abgeschlossen werden kann

        if success == -1:
            logger.error("Fehler beim Senden der Bestätigungsmail an: " + reg_email)
            return render_template("registration_no_success.html", info_danger=True, code=3, reg_email=reg_email)

        logger.success("Registrierung war erfolgreich für Benutzer: " + reg_email + ". Sende Bestätigungsmail...")
        return render_template("registration_success.html", reg_email=reg_email)


@app.route("/auth/admin/dashboard")
@app.route("/auth/dashboard")
def admin_dashboard():
    """
    Administrator-Dashboard. Erlaubt, Benutzer zu löschen.

    Nur zugänglich wenn man Administrator ist, also wenn die Sessionvariable is_admin = True. Zugriffe auf das
    Dashboard durch einen Benutzer der nicht als Administrator registriert ist, werden geloggt.

    Da es sich hier um sensitive Operationen mit der Datenbank handelt, wird aus Konsistenzgründen keine Validitätsprüfung auf die Session durchgeführt
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except KeyError as e:
        logger.error("Ein nicht eingeloggter Benutzer wollte auf das Admin Dashboard zugreifen.")
        return render_template("quick_info.html", info_danger=True, info_text="Du möchtest eine geschützte Seite aufrufen. Dieser Vorfall wird gemeldet.")
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

    # Benutzerdaten holen (Benutzer und Rollen)
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
    Ziel des Bestätigungslinks nach der Registrierung. Informationen zur Bestätigung wie token werden direkt per GET
    übergeben.

    Der Bestätigungsprozess läuft wie folgt ab:
    - Lade Confirm Token aus dem aufrufenden Link
    - Überprüfe in der zugehörigen Tabelle, ob das Token bekannt ist
        - Nicht bekannt (kein Eintrag): Fehler
        - Bekannt, aber bereits bestätigt: Meldung
        - Bekannt und nicht bestätigt: Erfolg
    - Setze verified in der Benutzertabelle von 3 (unverified) auf 4 (verified)
    """

    token = request.args.get("token")

    if not function_helper.check_params("token", str(token)):
        logger.error("Token konnte nicht ausgewertet werden (" + str(token) + ")")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Token konnte nicht ausgewertet werden. Bitte verändere nichts an dem Bestätigungslink.")

    db_handler = DB_Handler()
    (success, email) = db_handler.get_user_for_token(mysql,
                                                     token)  # Suche nach Benutzer basierend auf dem angegebenen Token
    if success == -1:
        logger.error("Unbekanntes Token wurde übergeben")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der Benutzer konnte nicht bestätigt werden!")

    if success == 2:
        logger.success("Benutzer '" + email + "' wurde bereits bestätigt")
        return render_template("quick_info.html", info_warning=True, info_text="Der Benutzer wurde bereits bestaetigt!")

    # Markiere Benutzer als bestätigt
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
    """
    Präsentiere Seite, um einen neuen Post zu schreiben.
    """
    return render_template("new_post.html", new_post_active="active")


@app.route("/auth/post_message", methods=["POST"])
def post_message():
    """
    Ziel nachdem ein neuer Post zur abgeschickt wurde. Aktion ist nur zugänglich für eingeloggte Mitglieder.
    Die Nachrichtenlänge ist auf 280 Zeichen beschränkt (angelehnt an Twitter).

    """

    try:
        session["logged_in"]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um eine Nachricht zu posten!")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Post sanitizen
    message = request.form["post_message"]
    hashtags = request.form["post_hashtags"]

    if not function_helper.check_params("text", message) or not function_helper.check_params("text", hashtags):
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnte deine Nachricht nicht gepostet werden. Bitte fülle alle Felder aus und versuche es erneut.")

    # Nur bestätigte Benutzer dürfen voten
    if not session["verified"]:
        logger.error(
            "Benutzer " + session[SESSIONV_USER] + " wollte Nachricht posten, ohne den Account bestätigt zu haben")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst deinen Account zuerst bestätigen, bevor du etwas posten kannst.")

    # Post in DB schreiben (post_message_to_db übernimmt Sanitizing der Nachricht)
    success = db_handler.post_message_to_db(mysql, session["uid"], None, message[:279], hashtags)

    if success == -1:
        logger.error("Post von Benutzer " + session[SESSIONV_USER] + " (" + message[
                                                                            :50] + "...)" + " konnte nicht gepostet werden (Datenbankfehler)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Nachricht konnte nicht geposted werden. Versuche es erneut!")
    elif success == 1:
        logger.success("Neue Nachricht von Benutzer " + session[SESSIONV_USER] + " geposted")
        return render_template("quick_info.html", info_success=True,
                               info_text="Deine Nachricht wurde geposted. Du kannst sie auf der Postseite nun sehen!")

    return "post message uid=" + str(
        session["uid"]) + " message=" + message + " hashtags=" + hashtags  # Programmfluss sollte hier nie ankommen


@app.route("/auth/vote")
def vote():
    """
    Ziel des Votes (Klick auf + oder - neben den Posts). Pro Benutzer ist maximal ein Vote erlaubt.
    """
    db_handler = DB_Handler()

    try:
        session["logged_in"]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True, info_text="Du musst eingeloggt sein, um zu voten!")

    # Session Timeout Handling
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Lese GET-Parameter
    method = request.args.get("method")
    post_id = request.args.get("post_id")
    uid = session["uid"]

    if not function_helper.check_params("text", method) or not function_helper.check_params("id", post_id):
        logger.error("Ungültiger Zugriff (Post ID oder Methode)")
        return render_template("quick_info.html", info_danger=True, info_text="Ungültige Post ID oder Zugriffsmethode!")

    if not method in ["upvote", "downvote"]:
        logger.error("Ungültiger Zugriff (Post ID oder Methode)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Art des Votes konnte nicht verstanden werden. Bitte verändere nichts am Link und versuche es erneut.")

    (code, data) = db_handler.check_if_already_voted(mysql, post_id,
                                                     uid)  # Überprüfe ob der Benutzer bereits für diesen Post abgestimmt hat

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
    csrf_seq = generate_token(8)

    # Gebe Seite mit vollstaendigem Post zurück
    # Praesentiere zufaellige Zeichenfolge, die eingegeben werden muss, um CSRF-Attacken zu unterbinden
    logger.success("Gebe Seite mit CSRF Token zurück. Warte auf Eingabe von Benutzer...")
    return render_template("vote.html", post=data, csrf_seq=csrf_seq, method=method,
                           method_label=method_labels[method])


@app.route("/auth/finish_vote", methods=["POST"])
def finish_vote():
    """
    Ziel nachdem das Bestätigungstoken für den Vote eingegeben wurde.
    """
    # Hole GET-Parameter
    csrf_token = request.args.get("csrf_token")
    post_id = request.args.get("post_id")
    method = request.args.get("method")
    input_csrf = request.form["vote_code"]
    uid = session["uid"]

    try:
        post_id_int = int(
            post_id)  # Überprüft, ob die über den Link übergebene Post-ID ein INT ist. Sollte nicht auf INT gecasted werden können, wird eine Exception geworfen was bedeutet, dass die Post-ID ungültig ist
    except:
        logger.error("Post ID konnte nicht zu INT umgewandelt werden. Möglicher Versuch einer SQL Injection erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")

    # Gültigkeitsprüfung der Parameter
    if not function_helper.check_params("text", input_csrf) or not function_helper.check_params("text",
                                                                                                csrf_token) or not function_helper.check_params(
        "id",
        post_id) or not method in [
        "upvote", "downvote"]:
        logger.error(
            "Request um den Vote abzuschließen wies ungültige Parameter(formen) auf. Vote kann nicht abgeschlossen werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")

    # Überprüfe csrf_seq
    if not csrf_token == input_csrf:
        logger.error("Vote konnte nicht abgeschlossen werden (keine Übereinstimmung der Token)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der eingegebene Code war leider falsch. Bitte versuche es erneut!")

    # Persistiere Vote
    db_handler = DB_Handler()

    # Session Timeout Handling
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

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


@app.route("/auth/controlpanel/change_email")
def change_email():
    """
    Präsentiere Seite um die E-Mail zu ändern. (nicht Reset)
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    return render_template("email_change.html")


@app.route("/auth/controlpanel/change_email_handler", methods=["POST"])
def change_email_handler():
    """
    Ziel nachdem das Formular der E-Mailänderung abgeschickt wurde. Überprüft die E-Mail u.A. auf korrektes Format.
    Nach erfolgreichen Checks wird der Change Request in die tralala_cp_change-Tabelle geschrieben und ist nun
    registriert. Durch die Bestätigung der Änderung mithilfe des Links aus der Bestätigungsmail wird die Änderung durchgeführt.

    Die Tabelle speichert folgende Informationen der Change Request:
    - Token (wird zur Bestätigung benötigt)
    - Requesttime (wann die Änderung angefragt wurde)
    - Action (Emailänderung oder Passwortänderung)
    - Data (Dafür benötigte Daten wie z.B. die neue E-Mail oder das neue Passwort)

    Diese Funktion kann nur von angemeldeten Benutzern ausgeführt werden.
    """

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
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

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
    token = generate_token(32)
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
    """
    Ziel des Bestätigungslink nach einer angeforderten Emailänderung.
    Überprüft die Gültigkeit des Tokens (also, ob ein solches in der Änderungstabelle bekannt ist) und lädt anschließend
    die Daten, die zu diesem Token gespeichert wurden (neue E-Mail).
    """

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
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

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

    db_handler.set_email_for_user(mysql, int(uid), new_email,
                                  app)  # Ändere E-Mail des Benutzers anhand der Daten aus der Änderungstabelle

    # Tabelle aufräumen
    db_handler.delete_cp_token(mysql, int(uid), "change_email")
    logger.success(
        "Benutzer " + str(uid) + " hat seine E-Mail geändert. Räume Tabelle mit alten Einträgen dieses Users auf...")

    delete_user_session()  # Automatischer Logout
    logger.debug("Logge User aus, um sich mit den neuen Credentials anzumelden.")

    return render_template("quick_info.html", info_success=True, info_text="Die E-Mail wurde geändert.")


@app.route("/auth/controlpanel/change_password")
def change_password():
    """
    Präsentiere Seite zum Ändern des Passworts.
    """
    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um diese Aktion durchführen zu dürfen")

    return render_template("password_change.html")


@app.route("/auth/controlpanel/change_password_handler", methods=["POST"])
def change_password_handler():
    """
    Ziel nachdem das Formular der Passwortänderung abgeschickt wurde. Überprüft das Passwort u.A. auf die vorgegebenen
    Passwortrichtlinien.
    Nach erfolgreichen Checks wird der Change Request in die tralala_cp_change-Tabelle geschrieben und ist nun
    registriert. Durch die Bestätigung der Änderung mithilfe des Links aus der Bestätigungsmail wird die Änderung durchgeführt.

    Die Tabelle speichert folgende Informationen der Change Request:
    - Token (wird zur Bestätigung benötigt)
    - Requesttime (wann die Änderung angefragt wurde)
    - Action (Emailänderung oder Passwortänderung)
    - Data (Dafür benötigte Daten wie z.B. die neue E-Mail oder das neue Passwort)

    Diese Funktion kann nur von angemeldeten Benutzern ausgeführt werden.
    """

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
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    user_email = session[SESSIONV_USER]
    curr_pass = db_handler.get_password_for_user(mysql, user_email)[
        1]  # Greife auf Index 1 zu, da Tupel zurückgegeben wird mit (1, "pbkdf2:sha256:xxx")
    uid = int(session[SESSIONV_UID])

    if not check_password_hash(curr_pass, old_pass):
        logger.error("Das eingegebene Passwort für Benutzer " + session[SESSIONV_USER] + " war falsch.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das eingegebene Passwort war falsch. Bitte versuche es erneut.")

    # Confirm Token in Datenbank festschreiben
    token = generate_token(32)
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
    """
    Ziel des Bestätigungslink nach einer angeforderten Passwortänderung.
    Überprüft die Gültigkeit des Tokens (also, ob ein solches in der Änderungstabelle bekannt ist) und lädt anschließend
    die Daten, die zu diesem Token gespeichert wurden (neues Passwort).
    """

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
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

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


@app.route("/reset_password1", methods=["POST"])
def reset_password1():
    """
    @deprecated
    """

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


@app.route("/auth/admin/delete_user", methods=["POST"])
def delete_user():
    """
     Administratorfunktion, um einen Benutzer zu löschen.
     Benötigt die Passwortbestätigung durch den Administrator, um CSRF-Attacken zu vermeiden.
    """

    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except KeyError as e:
        logger.error("Ein nicht eingeloggter Benutzer wollte /auth/admin/delete_user aufrufen.")
        return render_template("quick_info.html", info_danger=True, info_text="Du möchtest eine geschützte Seite aufrufen. Dieser Vorfall wird gemeldet.")
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
    if not check_if_valid_session(db_handler, session):
        return render_template("session_timeout.html",
                               timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

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
    """
    Präsentiert die Bestätigungsseite für die Durchführung einer Administratorfunktion.
    """

    try:
        session[SESSIONV_LOGGED_IN]  # Nur eingeloggte Benutzer dürfen Nachrichten posten
    except KeyError as e:
        logger.error("Ein nicht eingeloggter Benutzer wollte /auth/admin/confirm aufrufen.")
        return render_template("quick_info.html", info_danger=True, info_text="Du möchtest eine geschützte Seite aufrufen. Dieser Vorfall wird gemeldet.")
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

    if not function_helper.check_params("text", method) or not function_helper.check_params("id", obj):
        logger.error("obj konnte nicht zu INT umgewandelt werden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Auswertung der Parameter war fehlerhaft.")

    if not method in ["delete"]:
        logger.error("Unbekannte Methode. Erlaubt sind: delete")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ungültige Aktion. Bitte versuche es erneut.")

    logger.success(
        "Adminstratorfunktion wurde erfolgreich bestätigt. (Methode:" + str(method) + ", Objekt: " + str(obj))
    return render_template("confirm_admin.html", obj=obj, method=method)


@app.route("/reset/password")
def reset_password():
    """
    Präsentiert die Passwort-Reset Seite
    """
    return render_template("reset_password.html")


@app.route("/reset/password/handle", methods=["POST"])
def handle_password_reset():
    """
    Ziel nach Absenden des Passwort-Request Formulars. Überprüft die eingegebene E-Mail-Adresse auf Format.
    Ebenfalls wird überprüft, ob die eingegebene E-Mail im System registriert ist. Anschließend wird eine Reset-Mail an die
    angegebene E-Mail-Adresse geschickt.

    Um Spam-Attacken zu vermeiden, wurde die Anzahl der möglichen Resets innerhalb von 30 Minuten auf 5 Versuche beschränkt. Das
    Tracking erfolgt mittels der tralala_reset_password-Tabelle.

    Funktioniert nur bei nicht-eingeloggten Benutzern unter der Annahme, dass eingeloggte Benutzer ihr Passwort noch kennen.
    """

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
    token = function_helper.generate_token(32)
    db_handler.set_reset_token(mysql, token, uid, app)

    # Sende Reset Email
    function_helper.send_reset_mail(email, uid, token, url_for("confirm_password_reset"), app)

    logger.success("Anfrage für Passwort Reset wurde registriert. Sende Reset E-Mail an " + email)

    return render_template("quick_info.html", info_success=True,
                           info_text="Falls deine E-Mail Adresse bei uns registriert ist, haben wir dir eine E-Mail mit weiteren Anweisungen zum Vorgehen geschickt.")


@app.route("/reset/password/confirm_reset")
def confirm_password_reset():
    """
    Ziel des Links des Password-Resets. Überprüft das über die URL angegebene Token mit Einträgen in der Datenbank.
    Ist das Token richtig (= wurde in der Datenbank gefunden) wird ein Formular präsentiert, auf der das Passwort geändert werden kann.

    Das Token als auch die User-ID werden als Hidden Fields auf der Seite zur Änderung des Passworts eingetragen. Diese Felder
    werden unbedingt benötigt, um die Änderung festzuschreiben. Werden diese Werte verändert, wird der Reset nicht durchgeführt,
    da erneut überprüft wird, ob die Eingaben beim Absenden des Formulars verändert wurden oder nicht.
    """
    try:
        if session[SESSIONV_LOGGED_IN]:  # Nur eingeloggte Benutzer dürfen Nachrichten posten
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Du bist bereits eingeloggt. Du musst dich zuerst ausloggen, bevor du den Password Reset vervollständigen kannst.")
    except:
        pass

    token = request.args.get("token")
    uid = request.args.get("uid")

    if not function_helper.check_params("token", token) or not function_helper.check_params("id", uid):
        logger.error("Konnte die übergebenen URL-Parameter nicht auswerten.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine Anfrage nicht verstehen. Bitte ändere nichts an dem Link, den wir dir per Mail zugeschickt haben.")

    db_handler = DB_Handler()
    ref_token = db_handler.get_reset_token(mysql, uid)  # Suche nach zugehörigem Reset Token in der Datenbank

    if ref_token is None:
        logger.error("Kein zugehöriger Passwort Reset Request für Token " + str(ref_token) + " gefunden.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Es wurde kein zugehöriger Passwort Request in unserem System gefunden. Bitte versuche es erneut.")

    if not token == ref_token:
        logger.error(
            "Übermitteltes Token stimmt nicht mit registriertem Token überein. Mögliche Attacke (SQLi) erkannt.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten dein Token leider nicht bei uns im System finden. Bitte verändere nichts an dem Link, den wir die per Mail zugeschickt haben.")
    return render_template("password_reset_change.html", token=ref_token, uid=uid)


@app.route("/reset/password/set_new", methods=["POST"])
def set_new_password():
    """
    Handler der letztendlich das neue Passwort setzt.
    Hier wird erneut überprüft, ob das Token aus dem Hidden Field mit dem in der DB bekannten Token übereinstimmt. Ebenfalls
    wird ein Check auf die ID aus dem Hidden Field gemacht, ob auch diese verändert wurde. Nur wenn diese beiden Werte unverändert
    geblieben sind und einen zugehörigen Eintrag in der Datenbank haben, wird die Änderung des Passworts durchgeführt.
    """

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

    # Gibt Fehler zurück, sollte z.B. das Feld h_uid innerhalb des Formulars verändert worden sein
    if not ref_token == hidden_token:
        logger.error("Das übermittelte Reset Token stimmt leider nicht mit dem registrierten Token überein.")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das übermittelte Reset Token stimmt leider nicht mit dem uns bekannten Token überein. Es ist möglich, dass dieses während der Übertragung verändert wurde. Bitte versuche es erneut.")

    # Hole mit dem Token korrespondierendes Token aus der Datenbank
    (uid, token) = db_handler.get_reset_token(mysql, hidden_uid, "get_token_uid")

    # Schreibe neues Passwort (bzw. Hash des Passworts) in die Datenbank
    hashed_pass = generate_password_hash(new_pass)
    db_handler.set_pass_for_user(mysql, uid, hashed_pass, app)
    logger.success("Passwort für Benutzer " + str(uid) + " wurde geändert.")

    # Lösche Tokeneintrag aus der Datenbank
    db_handler.delete_pass_reset_token(mysql, uid, app)
    logger.debug("Logge Benutzer " + str(uid) + " aus, um sich mit den geänderten Credentials erneut einzuloggen.")

    return render_template("quick_info.html", info_success=True,
                           info_text="Dein Passwort wurde geändert. Du kannst dich nun einloggen.")


@app.route("/reset_password/action", methods=["POST"])
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
####################################################
"""


def delete_user_session():
    """
     Terminiere Benutzersession indem alle Sessionvariablen aus der Session gelöscht werden.
    """

    for sessionv in SESSIONV_ITER:
        session.pop(sessionv, None)


def check_for_session_state(uid):
    """
    Überprüfe den Status der aktuellen Benutzersitzung.

    - True: Der Benutzer ist noch eingeloggt und kann Aktionen durchführen
    - False: Die Sitzung des Benutzers ist außerhalb der Alive-Zeit (automatischer Timeout). Er wird bei der nächsten privilegierten
    Aktion automatisch ausgeloggt (=> wird durch Timeout-Handling Code innerhalb der Funktionen durchgeführt).
    """

    db_handler = DB_Handler()

    (code, data) = db_handler.check_session_state(mysql, uid)

    if code == 1:
        return True

    if code == -1:
        return False


def send_verification_email(reg_email):
    """
    Wrapper. Verwendet Implementierung aus function_helper. Sende Bestätigungsmail mit Verification Token.
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
        logger.error("Fehler beim Senden der Bestätigungsmail."
                     "..\n" + str(e))
        return -1

    logger.success("Bestätigungsemail gesendet an '" + reg_email + "' ...")
    return 1


def prepare_info_json(affected_url, info_text, additions):
    """
    Gebe eine Info- bzw. Fehlermeldung im JSON-Format zurUeck.
    Dictionary akzeptiert keine additions, falls folgende Keys in den
    additions existieren:
        - called_url
        - timestamp
        - info_text
    Durch eine Exception wird der dict merge abgebrochen.
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


def register_new_account(mysql, email, pw_hash, verification_token):
    db_handler = DB_Handler()
    success = db_handler.add_new_user(mysql, email, pw_hash, verification_token)

    return success


def check_if_valid_session(db_handler, session):
    """
    Der Session State wird pro autorisierbarer Aktion aktualisiert, sofern die aktuelle Session noch gültig ist, ansonsten wird die Session terminiert.
    Die Aktualisierung der Session bedeutet, dass session_start auf die aktuelle Zeit aktualisiert wird. session_max_alive wird auf session_start + MAX_SESSION_TIME gesetzt

    Der Session Timeout erfolgt nur, wenn MAX_SESSION_TIME lang keine Aktion ausgeführt wurde (wie z.B. eine Nachricht posten), die die Session refreshed hätte.
    """

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            logger.error("Session Timeout wurde erreicht. Automatischer Logout für Benutzer " + session[SESSIONV_USER])
            delete_user_session()
            return False
        else:
            # Refreshe den Session State
            db_handler.refresh_session_state(mysql, int(session[SESSIONV_UID]))
            return True


def sanitize_input(s):
    pass


"""
Errorhandler für HTTP-Errorcodes
####################################################
"""


@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for("index"))


@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template("quick_info.html", info_danger=True,
                           info_text="Unzulässige Zugriffsmethode auf die URL. Möglicherweise hast du eine URL aufgerufen, die nicht zum normalen Aufruf im Browser gedacht ist.")


"""
Einstiegspunkt
####################################################
"""

if __name__ == '__main__':
    app.secret_key = "e5ac358c-f0bf-11e5-9e39-d3b532c10a28"  # Wichtig für Sessions, da Cookies durch diesen Key signiert sind!
    logger.debug("Server Reload...")
    app.run(debug=True)
