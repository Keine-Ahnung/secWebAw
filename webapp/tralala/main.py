import random
import string

from flask import Flask, request, session, url_for, redirect, render_template
from db_handler import DB_Handler
from flaskext.mysql import MySQL
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["MYSQL_DATABASE_USER"] = "db_admin_tralala"
app.config["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
app.config["MYSQL_DATABASE_DB"] = "tralala"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

mysql = MySQL()
mysql.init_app(app)


@app.route("/")
def index():
    """
    Startseite
    """
    return render_template("index.html")


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
    """
    Überprüfe die Eingaben des Benutzers unabhängig von der clientseitigen Überprüfung.
    Sollten alle Eingaben korrekt sein, persistiere das neue Benutzerkonto in der Datenbank und schicke
    eine Bestätigungsemail an die angegebene Email.
    :return:
    """
    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"

        return prepare_info_json(url_for("post_user"), "called restricted HTTP method", return_info)

    else:
        reg_email = request.form["reg_email"]
        reg_password = request.form["reg_password"]
        reg_password_repeat = request.form["reg_password_repeat"]

        if reg_email == "" or reg_password == "" or reg_password_repeat == "":  # Reicht es, das allein durch JavaScript zu überprüfen?
            return prepare_info_json(url_for("post_user"), "some registration fields were left empty")

        # Hier überprüfen und ggf. sanitizen

        # Überprüfe, ob Password und Passwordwiederholung übereinstimmen
        if not reg_password == reg_password_repeat:
            app.logger.error("Passwort wurde nicht korrekt wiederholt")
            return render_template("registration_no_success.html", code=2)

        # Überprüfe, ob User schon existiert
        success = register_new_account(mysql, reg_email, generate_password_hash(reg_password),
                                       generate_verification_token(50))
        if success == -1:
            app.logger.error("Neuer Benutzer konnte nicht in die Datenbank geschrieben werden. Versuche es erneut")
            return render_template("registration_no_success.html", code=-1)
        elif success == 0:
            app.logger.error("Benutzer existiert bereits")
            return render_template("registration_no_success.html", code=0, reg_email=reg_email)

        app.logger.debug("Registrierung war erfolgreich. Benutzer wurde in die DB geschrieben (und Verification Token)")
        success = send_verification_email(reg_email)

        if success == -1:
            return render_template("registration_no_success.html", code=3, reg_email=reg_email)

        return render_template("registration_success.html", reg_email=reg_email)


@app.route("/admin/dashboard")
def admin_dashboard():
    """
    tbd
    """
    return render_template("admin.html")


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
        app.logger.error("Es konnte kein User for das Token '" + token + "' zurückgeliefert werden")
    if success == 2:
        app.logger.debug("Benutzer ist bereits bestätigt!")
        return render_template("quick_info.html", info_text="Der Benutzer wurde bereits bestätigt!")
    if success == 1:
        app.logger.debug("Account bestätigt für Benutzer '" + email + "' für Token '" + token + "'")

    # Setze Token auf Defaultwert und setze verified auf 1
    success = db_handler.user_successful_verify(mysql, email)

    if success == -1:
        app.logger.error("User konnte nicht bestätigt werden")
        return "User konnte nicht bestätigt werden"
    if success == 1:
        app.logger.debug("User wurde bestätigt")
        return render_template("quick_info.html", info_text="Der Benutzer wurde erfolgreich bestätigt!")


"""
Hilfsfunktionen, die keine HTTP Requests bearbeiten
"""


def generate_verification_token(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def send_verification_email(reg_email):
    """
        Sende Bestätigungsmail mit Verification Token.
    """

    app.logger.debug("Sende Bestätigungsmail.")

    # Hole Verification Token aus der DB
    db_handler = DB_Handler()
    (success, token) = db_handler.get_token_for_user(mysql, reg_email)

    if success == -1:
        return -1

    # Sende Bestätigungsemail mit Token
    sender = "verification_tralala@gmx.de"
    password = "sichwebapp_2017"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = reg_email
    msg["Subject"] = "Bestätige dein Account bei Tralala!"

    msg.attach(MIMEText(u"Hallo " + reg_email + "!</br>" \
                                                "Benutze den folgenden Link, um deinen Account zu bestaetigen. Du musst diesen in die Adresszeile deines Browsers kopieren.</br></br>" \
                                                "<a href=\"localhost:5000" + url_for(
        "confirm") + "?token=" + token + "\">" + "localhost:5000" + url_for(
        "confirm") + "?token=" + token + "</a>",
                        "html"))

    try:
        server = smtplib.SMTP("mail.gmx.net", 587)
        server.starttls()
        server.login(sender, password)

        server.sendmail(sender, reg_email, msg.as_string())
        server.quit()
    except Exception as e:
        app.logger.error("Fehler beim Senden der Bestätigungsmail...\n" + str(e))
        return -1

    app.logger.debug("Bestätigungsemail gesendet an '" + reg_email + "' ...")
    return 1


def prepare_info_json(affected_url, info_text, additions):
    """
        Gebe eine Info- bzw. Fehlermeldung im JSON-Format zurück.
        Dictionary akzeptiert keine additions, falls folgende Keys in den additions existieren:
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
