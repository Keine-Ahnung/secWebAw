from flask import Flask, request, session, url_for, redirect
from db_handler import DB_Handler
import json
import time

app = Flask(__name__)


@app.route("/")
def index():
    return "Willkommen auf Tralala!"


@app.route("/signup/post_user", methods=["POST", "GET"])
def post_user():
    if request.method == "GET":
        return_info = {}
        return_info["invalid_method"] = "GET"
        return_info["called_url"] = url_for("post_user")
        return_info["timestamp"] = str(time.ctime())

        return json.dumps(return_info, indent=4)


if __name__ == '__main__':
    app.run(debug=True)
