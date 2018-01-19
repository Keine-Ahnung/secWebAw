import random
import smtplib
import string

import db_handler
import security_helper
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail_basic(to, subject, text_mail_body, html_mail_body=None):
    """
    Method to send Mails using a gmx account
    """

    sender = "verification_tralala@gmx.de"
    password = "sichwebapp_2017"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(text_mail_body, 'plain'))

    if html_mail_body is not None:
        msg.attach(MIMEText(html_mail_body, 'html'))

    try:
        server = smtplib.SMTP("212.227.17.190", 587)
        server.starttls()
        server.login(sender, password)

        server.sendmail(sender, to, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(str(e))
        raise


def send_verification_mail(to, confirm_url):
    """
    Wrapper um eine Bestätigungsmail (Registrierung) zu senden.
    """

    subject = 'Bestaetige deinen Account bei Tralala!'

    html = """\
    <html>
        <head></head>
        <body>
            <p> Hallo """ + to + """\ </br>
            Benutze den folgenden Link, um deinen Account zu bestaetigen. </br>
            <a href=\"""" + confirm_url + """\"> Bestaetigung </a> </br> </br>
            Viel Freude, </br>
            dein Tralala- Team
            </p>
        </body>
    </html>
    """
    text = "Hallo " + to + "\nanbei der Link zur Bestaetigung deines " \
                           "Accounts\nkopiere diesen in deinen Browser, " \
                           "um deinen Account zu bestätigen\n\n" + confirm_url

    success = send_mail_basic(to=to, subject=subject, text_mail_body=text,
                              html_mail_body=html)

    return success


def send_reset_mail(to, uid, token, url, app):
    """
    Wrapper method to send the reset mail to an user.
    """

    mail_body_plain = "Wir haben dein Passwortanfrage erhalten.\n" \
                      "Bitte besuche den untenstehenden Link, um dein " \
                      "Passwort zurückzusetzen\n\n" + \
                      "http://localhost:5000" + str(url) + \
                      "?token=" + str(token) + "&uid=" + str(uid)

    try:
        send_mail_basic(to, "Tralala - Passwort zurücksetzen",
                        text_mail_body=mail_body_plain,
                        html_mail_body=None)
        app.logger.debug("Passwort Reset Mail gesendet an "
                         + to + " mit Token " + token)
        return True
    except Exception as e:
        return False


def reset_password(mysql, mail: str, url: str):
    """
    Method to reset the password of an existing user, by sending a mail to the
    mailaddress stored in the database
    """

    success, data = db_handler.check_for_existence(mysql=mysql, email=mail)
    if success != 1:
        return False
    else:
        token = generate_token(99)
        mysql.set_reset_token(mysql, token, data["uid"])
        mail_sended = send_reset_mail(data["email"], data["uid"], token, url)

    return mail_sended


def generate_token(length):
    """
    Generiere ein Verification Token der Länge length (String zufälliger Buchstaben und Zahlen)
    """

    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def compare_reset_token(mysql, userid: int, token: str):
    """
    Vergleiche das übergebene Reset Token mit dem in der Datenbank gespeicherten Reset Token.
    """

    token_database = db_handler.get_reset_token(mysql=mysql, userid=userid)

    if token == token_database:
        return True
    else:
        return False


def check_params(t, param):
    """
    Hilfsfunktion die das Format von Parametern überprüft, wie bspw. die Passwortstärke. Gibt True zurück, wenn die Evaluation erfolgreich war
    und False, wenn Abweichungen oder nicht-zugelassene Formate entdeckt wurden.

    Typen:
    - email
    - id
    - text
    - password
    """
    if t == "email":
        if not param:
            return False

        if not security_helper.check_mail(param):
            return False

        return True

    elif t == "id":
        if not param:
            return False

        try:
            int_p = int(param)
        except:
            return False

        if int_p < 0:
            return False

        return True

    elif t == "text":
        if not param:
            return False

        if param == "":
            return False

        return True

    elif t == "password":
        if not param:
            return False

        if param == "":
            return False

        if not security_helper.check_password_strength(param)[0]:
            return False

        return True

        return True

    elif t == "token":
        if not param:
            return False

        if param == "":
            return False

        if not param.isalnum():
            return False

        return True