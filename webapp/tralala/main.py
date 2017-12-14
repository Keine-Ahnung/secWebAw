import json
import random
import time

from flask import Flask, request, session, url_for, redirect, render_template
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

import function_helper
import security_helper
from db_handler import DB_Handler
from function_helper import generate_verification_token

app = Flask(__name__)

app.config["MYSQL_DATABASE_USER"] = "db_admin_tralala"
app.config["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
app.config["MYSQL_DATABASE_DB"] = "tralala"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

mysql = MySQL()
mysql.init_app(app)

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


@app.route("/")
def index():
    """
    Startseite
    Hier muss ebenfalls die Darstellung aller Posts aus der DB behandelt werden
    """

    db_handler = DB_Handler()
    (code, data) = db_handler.get_all_posts(mysql)

    if code == -1:
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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Benutzername und/oder Passwort sind inkorrekt!")
    elif code == -2:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst deinen Account bestätigen, bevor du dich einloggen kannst.")
    app.logger.debug("user found=" + data["email"] + ":" + data["password"])

    # UeberprUefe gehashte Passwoerter
    if not check_password_hash(data["password"], login_password):
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
        app.logger.debug("uid=" + str(session["uid"]))
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

    for sessionv in SESSIONV_ITER:
        session.pop(sessionv, None)

    return render_template("quick_info.html", info_success=True, info_text="Du wurdest erfolgreich ausgeloggt!")


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
    """
    UeberprUefe die Eingaben des Benutzers unabhaengig von der clientseitigen UeberprUefung.
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

        return prepare_info_json(url_for("post_user"), "GET ist unzulaessig für die Registration", return_info)

    else:
        reg_email = request.form["reg_email"]
        reg_password = request.form["reg_password"]
        reg_password_repeat = request.form["reg_password_repeat"]

        if reg_email == "" or reg_password == "" or reg_password_repeat == "":  # Reicht es, das allein durch JavaScript zu UeberprUefen?
            return prepare_info_json(url_for("post_user"), "Es wurden Felder bei der Registrierung leer gelassen")

        # Hier UeberprUefen und ggf. sanitizen

        if not security_helper.check_mail(reg_email):
            app.logger.error("Mailadresse nicht valide")
            return render_template("registration_no_success.html", info_danger=True, code=5)

        # UeberprUefe, ob Password und Passwordwiederholung übereinstimmen
        if not reg_password == reg_password_repeat:
            app.logger.error("Passwort wurde nicht korrekt wiederholt")
            return render_template("registration_no_success.html", info_danger=True, code=2)

        passed, comment = security_helper.check_password_strength(reg_password)
        if not passed:
            app.logger.error("Passwort nicht stark genug")
            return render_template("registration_no_success.html", info_danger=True, code=4, comment=comment)

        # UeberprUefe, ob User schon existiert
        success = register_new_account(mysql, reg_email, generate_password_hash(reg_password),
                                       generate_verification_token(50))
        if success == -1:
            app.logger.error("Neuer Benutzer konnte nicht in die Datenbank geschrieben werden. Versuche es erneut")
            return render_template("registration_no_success.html", info_danger=True, code=-1)
        elif success == 0:
            app.logger.error("Benutzer existiert bereits")
            return render_template("registration_no_success.html", info_danger=True, code=0, reg_email=reg_email)

        app.logger.debug("Registrierung war erfolgreich. Benutzer wurde in die DB geschrieben (und Verification Token)")
        success = send_verification_email(reg_email)

        if success == -1:
            return render_template("registration_no_success.html", info_danger=True, code=3, reg_email=reg_email)

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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt und Administrator sein, um diese Aktion durchführen zu dürfen")

    if not session[SESSIONV_ADMIN]:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    # Benutzerdaten holen
    db_handler = DB_Handler()
    (code_users, users) = db_handler.get_all_users(mysql)
    (code_roles, roles) = db_handler.get_all_roles(mysql)

    if code_users == -1 or code_roles == -1:
        return render_template("admin.html",
                               error="Admin Dashboard konnte nicht geladen werden. Versuche es später noch einmal.")

    # In Dashboard eintragen
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
        app.logger.error(
            "Es konnte kein User for das Token '" + token + "' zurückgeliefert werden (ungültiges Token)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der Benutzer konnte nicht bestaetigt werden!")

    if success == 2:
        app.logger.debug("Benutzer ist bereits bestaetigt!")
        return render_template("quick_info.html", info_warning=True, info_text="Der Benutzer wurde bereits bestaetigt!")

    if success == 1:
        app.logger.debug("Account bestaetigt für Benutzer '" + email + "' fUer Token '" + token + "'")

    # Setze Token auf Defaultwert und setze verified auf 1
    success = db_handler.user_successful_verify(mysql, email)

    if success == -1:
        app.logger.error("User konnte nicht bestaetigt werden (Benutzer konnte in der DB nicht bestaetigt werden)")
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der Benutzer konnte nicht bestätigt werden!")

    if success == 1:
        app.logger.debug("User wurde bestaetigt")
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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst deinen Account zuerst bestätigen, bevor du etwas posten kannst.")

    # Post in DB schreiben
    success = db_handler.post_message_to_db(mysql, session["uid"], None, message[:279], hashtags)

    if success == -1:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Nachricht konnte nicht geposted werden. Versuche es erneut!")
    elif success == 1:
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
        session["logged_in"]  # Nur eingeloggte Benutzer dUerfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True, info_text="Du musst eingeloggt sein, um zu voten!")

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            delete_user_session()
            return render_template("session_timeout.html",
                                   timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    # Lese GET-Parameter
    method = request.args.get("method")
    post_id = request.args.get("post_id")
    uid = session["uid"]

    if post_id == "" or method == "":
        return render_template("quick_info.html", info_danger=True, info_text="Ungültige Post ID oder Zugriffsmethode!")

    (code, data) = db_handler.check_if_already_voted(mysql, post_id, uid)

    if code == -1:
        return render_template("quick_info.html", info_warning=True,
                               info_text="Du hast bereits für diesen Post gevoted.")

    # Hole Post aus DB
    (code, data) = db_handler.get_post_by_pid(mysql, post_id)

    if code == -1:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keinen Post mit der ID " + str(post_id) + " finden!")

    method_labels = {"upvote": "Upvote", "downvote": "Downvote"}
    csrf_seq = generate_verification_token(8)

    # Gebe Seite mit vollstaendigem Post zurUeck
    # Praesentiere zufaellige Zeichenfolge, die eingegeben werden muss, um CSRF-Attacken zu unterbinden
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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")

    if input_csrf == "" or csrf_token == "" or post_id == "" or post_id_int < 0 or not method in ["upvote", "downvote"]:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Deine Anfrage war ungültig. Bitte versuche es erneut!")
    # Ueberprüfe csrf_seq
    if not csrf_token == input_csrf:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Der eingegebene Code war leider falsch. Bitte versuche es erneut!")

    # Persistiere Vote
    db_handler = DB_Handler()

    (code, data) = db_handler.check_if_already_voted(mysql, post_id, uid)

    if code == -1:
        return render_template("quick_info.html", info_warning=True,
                               info_text="Du hast bereits für diesen Post gevoted.")

    if method == "upvote":
        # Registriere Upvote
        success_register = db_handler.register_vote(mysql, post_id, uid, "upvote")

        # Poste Upvote
        success = db_handler.do_upvote(mysql, post_id)
        if success == -1 or success_register == -1:
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Etwas ist schiefgelaufen! Versuche es erneut!")
        return render_template("quick_info.html", info_success=True, info_text="Upvote erfolgreich!")

    elif method == "downvote":
        # Registriere Downvote
        success_register = db_handler.register_vote(mysql, post_id, uid, "downvote")

        # Poste Downvote
        success = db_handler.do_downvote(mysql, post_id)
        if success == -1 or success_register == -1:
            return render_template("quick_info.html", info_danger=True,
                                   info_text="Etwas ist schiefgelaufen! Versuche es erneut!")
        return render_template("quick_info.html", info_success=True, info_text="Downvote erfolgreich!")


@app.route("/auth/controlpanel/change-email")
def change_email():
    """
    tbd
    """
    try:
        session["logged_in"]  # Nur eingeloggte Benutzer dUerfen Nachrichten posten
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst eingeloggt sein, um deine Email zu ändern.")

    db_handler = DB_Handler()

    # Session Timeout Handling
    if session["logged_in"]:
        if not check_for_session_state(session["uid"]):  # wenn False zurückgegeben wird, ist der Timeout erreicht
            db_handler.invalidate_session(mysql, session["uid"])
            delete_user_session()
            return render_template("session_timeout.html",
                                   timeout_text="Du wurdest automatisch ausgeloggt. Melde dich erneut an")

    return render_template("quick_info.html", info_success=True, info_text="Email ändern")


@app.route("/auth/controlpanel/change-password")
def change_password():
    """
    tbd
    """
    return render_template("quick_info.html", info_success=True, info_text="Passwort ändern")


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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    uid = request.args.get("uid")
    password = request.form["password"]

    try:
        int(uid)
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="User ID muss ein INT sein.")

    if not password:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Bitte gebe ein Passwort ein.")

    db_handler = DB_Handler()

    # Überprüfe, ob Passwork korrekt
    (code, data) = db_handler.get_password_for_user(mysql, session[SESSIONV_USER])

    if code == -1:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Konnte Benutzerdaten nicht abrufen. Bitte versuche es erneut.")

    if not check_password_hash(data, password):
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das eingegebene Passwort war ungültig.")

    (code, e) = db_handler.delete_user(mysql, int(uid))

    if code == -1:
        app.logger.debug("Fehler beim Löschen eines Benutzers:\n" + str(e))
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ein unerwarteter Fehler ist aufgetreten.")
    elif code == 1:
        return render_template("quick_info.html", info_success=True,
                               info_text="Benutzer (UID: " + str(uid) + ") wurde gelöscht.")
    else:
        app.logger.debug("Fehler beim Löschen eines Benutzers:\n" + str(e))
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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du musst Administrator sein, um diese Aktion durchführen zu dürfen")

    method = request.args.get("method")
    obj = request.args.get("obj")

    try:
        int(obj)
    except:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Objekt muss ein INT sein.")

    if not method in ["delete"]:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Ungültige Aktion. Bitte versuche es erneut.")

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

    if not email or not security_helper.check_mail(email):
        return render_template("quick_info.html", info_danger=True,
                               info_text="Die E-Mail besitzt ein ungültiges Format. Bitte versuche es erneut.")

    db_handler = DB_Handler()

    # Überprüfe, ob Account mit angegebener E-Mail existiert
    (code, data) = db_handler.check_for_existence(mysql, email)
    if code != 1:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Wir konnten leider keinen Account mit der angegebenen E-Mail finden. Bitte Überprüfe die E-Mail und versuche es erneut.")

    uid = data["uid"]

    # Überprüfe auf Spam Attacke bzw. zu viele Passwort Resets
    if not db_handler.count_password_requests(mysql, int(uid), app):
        return render_template("quick_info.html", info_danger=True,
                               info_text="Du hast zu oft versucht dein Passwort zurückzusetzen, weshalb wir dieses Feature für dich vorübergehend deaktiviert haben, um mögliche Spam-Attacken zu verhindern. Vielen Dank für dein Verständnis.")

    # Persistiere Reset Token
    token = function_helper.generate_verification_token(32)
    db_handler.set_reset_token(mysql, token, uid, app)

    # Sende Reset Email
    function_helper.send_reset_mail(email, uid, token, url_for("confirm_password_reset"), app)

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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Leider konnten wir deine Anfrage nicht verstehen. Bitte ändere nichts an dem Link, den wir dir per Mail zugeschickt haben.")

    db_handler = DB_Handler()
    ref_token = db_handler.get_reset_token(mysql, uid)

    if ref_token is None:
        return render_template("quick_info.html", info_danger=True,
                               info_text="Es wurde kein zugehöriger Passwort Request in unserem System gefunden. Bitte versuche es erneut.")

    if not token == ref_token:
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
        return render_template("quick_info.html", info_danger=True,
                               info_text="Das übermittelte Reset Token stimmt leider nicht mit dem uns bekannten Token überein. Es ist möglich, dass dieses während der Übertragung verändert wurde. Bitte versuche es erneut.")

    # Hole mit dem Token korrespondierendes Token aus der Datenbank
    (uid, token) = db_handler.get_reset_token(mysql, hidden_uid, "get_token_uid")

    # Schreibe neues Passwort in die Datenbank
    hashed_pass = generate_password_hash(new_pass)
    db_handler.set_pass_for_user(mysql, uid, hashed_pass, app)

    # Lösche Tokeneintrag aus der Datenbank
    db_handler.delete_pass_reset_token(mysql, uid, app)

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


"""
    Zugriff auf die DB mit der DB_Handler Klasse
"""


def register_new_account(mysql, email, pw_hash, verification_token):
    db_handler = DB_Handler()
    success = db_handler.add_new_user(mysql, email, pw_hash, verification_token)

    return success


if __name__ == '__main__':
    app.secret_key = "e5ac358c-f0bf-11e5-9e39-d3b532c10a28"  # Wichtig für Sessions, da Cookies durch diesen Key signiert sind!
    app.run(debug=True)
