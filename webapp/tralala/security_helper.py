import bleach
import re

'''
Method to replace the html entries in the messages.
We will stay with the <br> as long as we thought about something new. 
'''


def clean_messages(message_text):
    return bleach.clean(message_text, tags=['br', 'b', 'i', 'strong'])


''''
Method to replace unwanted in the hashtags
Will replace : # because we don't want to have ##
Will replace : everything what looks like html 
'''


def clean_hashtags(hashtags_text):
    html_cleaned = bleach.clean(hashtags_text)

    hashtag_list = html_cleaned.split(' ')  # string.replace would be possible although. should talk about that

    if '#' in hashtag_list:
        hashtag_list.remove('#')

    return ','.join(hashtag_list)


'''
Method to check the passwords
Splitted into two parts. 
First part for passwords longer than 15 chars (nist reco)
Second part for passwords between 10 and 15 chars

'''


def check_password_strength(password_text):

    if len(password_text) >= 15:
        if re.search('[a-z]+', password_text) and re.search('[A-Z]+', password_text):
            return True, "nist"

    elif 10 < len(password_text) < 15:
        special_chars = {'!', '"', '§', '$', '%', '&', '/', '(', ')', '=', '?'}

        if not re.search('[a-z]+', password_text):
            return False, "charset Lower"

        if not re.search('[A-Z]+', password_text):
            return False, "chartset Upper"

        if not re.search('[0-9]+', password_text):
            return False, "charset Numbers"

        if not any(spec_char in special_chars for spec_char in password_text):
            return False, "special chars"

        return True, "not nist"

    return False, "to short"


'''
Method to validate the mailaddress
regex gemopst bei https://www.scottbrady91.com/Email-Verification/Python-Email-Verification-Script
'''


def check_mail(mailaddress):
    success = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', mailaddress)

    if success:
        return True
    else:
        return False
