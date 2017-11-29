from flask import Flask, request, session, url_for, redirect
from db_handler import DB_Handler
import json
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


@app.route("/")
def index():
    return "Willkommen auf Tralala!"


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"

        return prepare_info_json(url_for("post_user"), "called restricted HTTP method", return_info)

    else:
        reg_username = request.form["reg_username"]
        reg_email = request.form["reg_email"]
        reg_password = generate_password_hash(request.form["reg_password"])

        if reg_username == "" or reg_email == "" or reg_password == "":  # Reicht es, das allein durch JavaScript zu überprüfen?
            return prepare_info_json(url_for("post_user"), "some registration fields were left empty")

        # Hier überprüfen und ggf. sanitizen
        


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


if __name__ == '__main__':
    app.secret_key = "e5ac358c-f0bf-11e5-9e39-d3b532c10a28"  # Wichtig für Sessions, da Cookies durch diesen Key signiert sind!
    app.run(debug=True)
