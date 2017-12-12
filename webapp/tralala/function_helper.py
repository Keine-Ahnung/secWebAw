import random
import smtplib
import string

import db_handler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

'''
Method to send Mails using a gmx account

'''


def send_mail_basic(to, subject, text_mail_body, html_mail_body=None):
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

'''
Method to send the reset mail to an user.
'''


def send_reset_mail(to, uid, token, url):
    mail_body_plain = "Your password reset request was confirmed.\n" \
                      "Click the following link to reset the password\n\n"
    + url + "/?token=" + token + "&uid=" + uid

    try:
        send_mail_basic(to, "Password reset", text_mail_body=mail_body_plain,
                    html_mail_body=None )
        return True
    except Exception as e:
        return False


'''
Method to reset the password of an existing user, by sending a mail to the 
mailaddress stored in the database
'''


def reset_password(mysql: db_handler.DB_Handler, mail: str, url: str):

    success, data = mysql.check_for_existence(mysql=mysql, email=mail)
    if success != 1:
        return False
    else:
        token = generate_verification_token(99)
        mysql.set_reset_token(mysql, token, data["uid"])
        mail_sended = send_reset_mail(data["email"], data["uid"], token, url)

    return mail_sended

def generate_verification_token(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def compare_reset_token(mysql: db_handler.DB_Handler, userid: int, token: str):
    token_database = mysql.get_reset_token(mysql=mysql, userid=userid)

    if token == token_database:
        return True
    else:
        return False
