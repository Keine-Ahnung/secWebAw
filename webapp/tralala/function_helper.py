import smtplib
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

