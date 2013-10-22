#!/usr/bin/env python
# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>
import os
import time
import json
import urllib2, urllib
import fnmatch
import cgi
from trello_hipchat_config import (TRELLO_API_KEY, TRELLO_TOKEN,
                                   HIPCHAT_API_KEY, MONITOR, HIPCHAT_COLOR)
from messages import MESSAGES
from .util import to_trello_date, from_trello_date

DEBUG = False
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    PREV_ID = long(open(ROOT_DIR + "/last-action.id").read(), 16)
except IOError:
    PREV_ID = 0
LAST_ID = 0
LAST_TIME = time.time() - 20*60

ESC = cgi.escape


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


def msg(room_id, message, mtype="html"):
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


def trunc(string, maxlen=200):
    """
    If the string is longer than maxlen characters, return a truncated version,
    otherwise return the string unchanged.
    """
    if len(string) >= maxlen:
        string = string[:maxlen] + "[...]"
    return string


def card_in_lists(name, list_names):
    """
    Return True if name matches any of the list_names (which can be contain
    some regular expression syntax (the same as what can be used in the Unix
    shell)), otherwise False.
    """
    for filt in list_names:
        if name == filt or fnmatch.fnmatch(name, filt):
            return True
    return False


def notify(board_id, list_names, room_id, include_actions=["all"]):
    """
    Look up the recent actions for the Trello board, and report all of the
    relevant ones to the HipChat room.
    """
    global LAST_ID, LAST_TIME

    since = to_trello_date(LAST_TIME)
    if DEBUG:
        print 'getting actions since', since
    actions = trello("/boards/%s/actions" % board_id,
                     filter=','.join(include_actions))
#                     since=since)
    if not actions:
        print 'there are no actions!'
        return

    # Iterate over the actions, in reverse order because of chronology.
    for A in reversed(actions):

        if DEBUG:
            print A
            print '\n\n\n'

        # If this is older than the last one we already reported, ignore it.
        if long(A["id"], 16) <= PREV_ID:
            continue

        date = from_trello_date(A["date"])
        LAST_TIME = max(LAST_TIME, date)

        action_type = A['type']

        params = {'author': ESC(A["memberCreator"]["fullName"])}

        if "card" in A["data"]:
            card_id_short = A["data"]["card"]["idShort"]
            card_id = A["data"]["card"]["id"]
            params['card_url'] = ("https://trello.com/card/%s/%s/%s"
                        % (card_id, board_id, card_id_short))
            params['card_name'] = ESC(A["data"]["card"]["name"])

        if action_type == "createCard":
            list_name = trello("/cards/%s/list" % card_id)["name"]
            if not card_in_lists(list_name, list_names):
                continue

        elif action_type == "commentCard":
            list_name = trello("/cards/%s/list" % card_id)["name"]
            if not card_in_lists(list_name, list_names):
                continue
            params['text'] = trunc(" ".join(A["data"]["text"].split())) 

        elif action_type == "addAttachmentToCard":
            list_name = trello("/cards/%s/list" % card_id)["name"]
            if not card_in_lists(list_name, list_names):
                continue        
            
            params['attachment_name'] = ESC(A["data"]["attachment"]["name"])
            params['attachment_url'] = A["data"]["attachment"]["url"]

        elif action_type == "updateCard":
            if "idList" in A["data"]["old"] and \
               "idList" in A["data"]["card"]:
                # Move between lists
                old_list_id = A["data"]["old"]["idList"]
                new_list_id = A["data"]["card"]["idList"]
                old_list_name = trello("/list/%s" % old_list_id)["name"]
                new_list_name = trello("/list/%s" % new_list_id)["name"]

                if not (card_in_lists(old_list_name, list_names) or
                        card_in_lists(new_list_name, list_names)):
                    continue
                params['old_list'] = ESC(old_list_name)
                params['new_list'] = ESC(new_list_name)
            else:
                continue

        elif action_type == "updateCheckItemStateOnCard":
            list_name = trello("/cards/%s/list" % card_id)["name"]
            if not card_in_lists(list_name, list_names):
                continue

            params['item_name'] = ESC(A["data"]["checkItem"]["name"])
            # Why separate these into two different "action types" rather than
            # putting it in the format string?  So that later we can change it
            # to ignore unchecking if we want.
            if A["data"]["checkItem"]["state"] == "complete":
                action_type += "-check"
            else:
                action_type += "-uncheck"

        elif action_type == "createList":
            params["list_name"] = ESC(A["data"]["list"]["name"])
            params["board_name"] = ESC(A["data"]["board"]["name"])
            params["board_url"] = "https://trello.com/b/%s/" % board_id

        else:
            # This is an action that we haven't written a template for yet.
            continue

        msg(room_id, MESSAGES[action_type] % params)

    LAST_ID = max(LAST_ID, long(A["id"], 16))


if __name__ == "__main__":
    while True:
        print 'starting another round\n\n\n'
        for (board_id, parameters) in MONITOR:
            notify(board_id, **parameters)
        time.sleep(60)
    open(ROOT_DIR + "/last-action.id", "w").write(hex(LAST_ID))
