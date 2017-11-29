from flask import Flask, request, session, url_for, redirect, render_template
from db_handler import DB_Handler
from flaskext.mysql import MySQL
import json
import time
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
    return render_template("index.html")


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
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

        # Überprüfe ob User schon existiert
        print("reg_data=" + reg_email + ":" + reg_password + ":" + reg_password_repeat)
        print("pw_hash=" + generate_password_hash(reg_password))
        success = register_new_account(mysql, reg_email, generate_password_hash(reg_password))
        if success == -1:
            app.logger.error("Neuer Benutzer konnte nicht in die Datenbank geschrieben werden. Versuche es erneut")
            return render_template("registration_no_success.html", code=-1)
        elif success == 0:
            app.logger.error("Benutzer existiert bereits")
            return render_template("registration_no_success.html", code=0, reg_email=reg_email)

        app.logger.debug("Registrierung war erfolgreich. Benutzer wurde in die DB geschrieben")
        send_verification_email(reg_email)
        return render_template("registration_success.html", reg_email=reg_email)


@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin.html")


def send_verification_email(reg_email):
    app.logger.debug("Sende Bestätigungsemail an '" + reg_email + "' ...")


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


def register_new_account(mysql, email, pw_hash):
    db_handler = DB_Handler()
    success = db_handler.add_new_user(mysql, email, pw_hash)

    return success


if __name__ == '__main__':
    app.secret_key = "e5ac358c-f0bf-11e5-9e39-d3b532c10a28"  # Wichtig für Sessions, da Cookies durch diesen Key signiert sind!
    app.run(debug=True)
