import urllib2, urllib
import json
from trello_hipchat_config import (TRELLO_API_KEY, TRELLO_TOKEN,
                                   HIPCHAT_API_KEY, HIPCHAT_COLOR)

DEBUG = False

def trello(path, **kwargs):
    """
    Make a request to the Trello API.
    """
    kwargs["key"] = TRELLO_API_KEY
    try:
        kwargs["token"] = TRELLO_TOKEN
    except NameError:
        # There is no Trello token, that's okay.
        pass
    
    url = "https://api.trello.com/1" + path + "?" + urllib.urlencode(kwargs)
    req = urllib2.urlopen(url)
    data = req.read()
    return json.loads(data)


def hipchat_msg(room_id, message, mtype="html"):
    """
    Send a message to HipChat.
    """
    if DEBUG:
        print 'message:', message.encode("utf-8")
        print '\n\n\n'
        return 

    data = {
        "from": "Trello",
        "message": message.encode("utf-8"),
        "message_format": mtype,
        "color": HIPCHAT_COLOR,
        "room_id": room_id
    }
    
    data = urllib.urlencode(data)
    req = urllib2.urlopen("https://api.hipchat.com/v1/rooms/message?format=json&auth_token=%s" % HIPCHAT_API_KEY, data)
    req.read()
