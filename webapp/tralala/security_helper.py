import html
import re


def clean_messages(message_text):
    """
    Method to replace the html entries in the messages.
    We will stay with the <br> as long as we thought about something new.
    """

    return html.escape(message_text)
    # return bleach.clean(message_text, tags=bleach.ALLOWED_TAGS) # zu liberal?


def clean_hashtags(hashtags_text):
    """
    Method to replace unwanted in the hashtags
    Will replace : # because we don't want to have ##
    Will replace : everything what looks like html
    """

    html_cleaned = html.escape(hashtags_text)

    hashtag_list = "".join(html_cleaned.split()).split(',')

    if '#' in hashtag_list:
        hashtag_list.remove('#')

    if '' in hashtag_list:
        hashtag_list = list(filter(None, hashtag_list))

    return ','.join(hashtag_list)


def check_password_strength(password_text):
    """
    Method to check the passwords
    Splitted into two parts.
    First part for passwords longer than 15 chars (nist reco)
    Second part for passwords between 10 and 15 chars
    """

    special_chars = {'.', '_', '!', '"', '§', '$', '%', '&', '/', '(', ')',
                     '=', '?'}

    if len(password_text) >= 8 and len(password_text) <= 24:
        if not re.search('[a-zA-Z0-9]+', password_text) and not any(
                spec_char in special_chars for spec_char in password_text):
            return False, "Das Passwort enthält keine Buchstaben/Zahlen " \
                          "oder " \
                          "Sonderzeichen."
        else:
            return True, "Das Passwort entspricht unserern" \
                         " Sicherheitsrichtlinien."
    else:
        return False, "Leider war das Passwort nicht innerhalb der" \
                      " vorgegebenen Länge (Mindestens 8 Zeichen, " \
                      "höchstens 24 Zeichen)."


def check_mail(mailaddress):
    """
    Method to validate the mailaddress
    regex gemopst bei https://www.scottbrady91.com/Email-Verification/
    Python-Email-Verification-Script
    """
    
    mod_ma = mailaddress.lower()
    success = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)'
                       '*(\.[a-z]{2,4})$', mod_ma)

    if success:
        return True
    else:
        return False
