import bleach


'''
Method to replace the html entries in the messages.
We will stay with the <br> as long as we thought about something new. 
'''
def clean_messages(messageText):
    return bleach.clean(messageText, tags=['br', 'b', 'i', 'strong'])


''''
Method to replace unwanted in the hashtags
Will replace : # because we don't want to have ##
Will replace : everything what looks like html 
'''
def clean_hashtags(hashtagsText):
    htmlCleaned = bleach.clean(hashtagsText)

    hashtagList = htmlCleaned.split(',') # string.replace would be possible although. should talk about that
    hashtagList.remove('#')

    return ','.join(map(str,hashtagList))


