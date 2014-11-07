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

from __future__ import print_function
import os
import sys
import time
import calendar
import json
import fnmatch

if sys.version_info.major > 2:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from html import escape
else:
    from urllib import urlencode, urlopen
    from cgi import escape as cgi_escape
    escape = lambda string: cgi_escape(string, quote=True)

from trello_hipchat_config import (TRELLO_API_KEY, TRELLO_TOKEN,
                                   HIPCHAT_API_KEY, MONITOR, HIPCHAT_COLOR)
from messages import MESSAGES

DEBUG = True
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    LAST_ID = int(open(ROOT_DIR + '/last-action.id').read())
except IOError:
    LAST_ID = 0
# Don't check back in time more than 20 minutes ago.
LAST_TIME = time.time() - 20*60


def to_trello_date(timestamp):
    """
    Take a timestamp (number of seconds since the epoch) and turn it into a
    string in Trello's date format.
    """
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp))


def from_trello_date(string):
    """
    Take a string in Trello's date format and turn it into a timestamp (number
    of seconds since the epoch).
    """
    return calendar.timegm(time.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ'))


def trello(path, **kwargs):
    """
    Make a request to the Trello API.
    """
    kwargs['key'] = TRELLO_API_KEY
    if TRELLO_TOKEN:
        kwargs['token'] = TRELLO_TOKEN

    url = 'https://api.trello.com/1' + path + '?' + urlencode(kwargs)
    req = urlopen(url)
    data = req.read().decode('utf-8')
    return json.loads(data)


def msg(room_id, message, mtype='html'):
    """
    Send a message to HipChat.
    """
    if DEBUG:
        print('message:', message.encode('utf-8'))
        print('\n\n\n')
        return 

    data = {
        'from': 'Trello',
        'message': message.encode('utf-8'),
        'message_format': mtype,
        'color': HIPCHAT_COLOR,
        'room_id': room_id
    }

    data = urlencode(data)
    req = urlopen('https://api.hipchat.com/v1/rooms/message?format=json&auth_token=%s' % HIPCHAT_API_KEY, data)
    req.read()


def trunc(string, maxlen=200):
    """
    If the string is longer than maxlen characters, return a truncated version,
    otherwise return the string unchanged.
    """
    if len(string) >= maxlen:
        string = string[:maxlen - 5] + '[...]'
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


def notify(board_id, list_names, room_id, include_actions=['all'], filters=[]):
    """
    Look up the recent actions for the Trello board, and report all of the
    relevant ones to the HipChat room.
    """
    global LAST_ID, LAST_TIME

    since = to_trello_date(LAST_TIME)
    if DEBUG:
        print('getting actions since', since)
    actions = trello('/boards/%s/actions' % board_id,
                     filter=','.join(include_actions),
                     since=since)
    if not actions:
        print('there are no actions!')
        return

    # Iterate over the actions, in reverse order because of chronology.
    for A in reversed(actions):

        if DEBUG:
            print(A)
            print('\n\n\n')

        # If this is older than the last one we already reported, ignore it.
        if int(A['id'], 16) <= LAST_ID:
            continue

        # If this doesn't pass the filters, ignore it.
        if not all(f(A) for f in filters):
            continue

        date = from_trello_date(A['date'])
        LAST_TIME = max(LAST_TIME, date)

        action_type = A['type']

        params = {'author': escape(A['memberCreator']['fullName']),
                  'action_type': action_type}

        # Basic info for applicable card/list/board

        if 'card' in A['data'] and action_type != 'deleteCard':
            card_id = A['data']['card']['id']
            params['card_url'] = ('https://trello.com/c/%s/' % card_id)
            params['card_name'] = escape(A['data']['card']['name'])

        if 'list' in A['data']:
            params['list_name'] = escape(A['data']['list']['name'])

        if 'board' in A['data']:
            params['board_name'] = escape(A['data']['board']['name'])
            params['board_url'] = 'https://trello.com/b/%s/' % board_id

        # Specific action types

        if action_type == 'createCard':
            list_name = trello('/cards/%s/list' % card_id)['name']
            if not card_in_lists(list_name, list_names):
                continue

        elif action_type == 'commentCard':
            list_name = trello('/cards/%s/list' % card_id)['name']
            if not card_in_lists(list_name, list_names):
                continue
            params['text'] = trunc(' '.join(A['data']['text'].split()))

        elif action_type in ('addMemberToCard', 'removeMemberFromCard'):
            params['member'] = A['member']['fullName']

        elif action_type == 'addAttachmentToCard':
            list_name = trello('/cards/%s/list' % card_id)['name']
            if not card_in_lists(list_name, list_names):
                continue        
            
            params['attachment_name'] = escape(A['data']['attachment']['name'])
            params['attachment_url'] = A['data']['attachment']['url']

        elif action_type == 'updateCard':
            if 'idList' in A['data']['old'] and \
               'idList' in A['data']['card']:
                # Move between lists
                old_list_id = A['data']['old']['idList']
                new_list_id = A['data']['card']['idList']
                old_list_name = trello('/list/%s' % old_list_id)['name']
                new_list_name = trello('/list/%s' % new_list_id)['name']

                if not (card_in_lists(old_list_name, list_names) or
                        card_in_lists(new_list_name, list_names)):
                    continue
                params['old_list'] = escape(old_list_name)
                params['new_list'] = escape(new_list_name)
                action_type += '-move'
            else:
                # Some other type of card update, such as renaming(?) or archiving. (TODO)
                action_type = 'default'

        # TODO: probably want to check card_in_lists for these next two?
        elif action_type in ('moveCardFromBoard', 'moveListFromBoard'):
            params['to_board_url'] = ('https://trello.com/b/%s/' %
                                      A['data']['boardTarget']['id'])
            params['to_board_name'] = escape(A['data']['boardTarget']['name'])

        elif action_type == ('moveCardToBoard', 'moveListToBoard'):
            params['from_board_url'] = ('https://trello.com/b/%s/' %
                                        A['data']['boardSource']['id'])
            params['from_board_name'] = escape(A['data']['boardSource']['name'])

        elif action_type == 'updateCheckItemStateOnCard':
            list_name = trello('/cards/%s/list' % card_id)['name']
            if not card_in_lists(list_name, list_names):
                continue

            params['item_name'] = escape(A['data']['checkItem']['name'])
            # Why separate these into two different 'action types' rather than
            # putting it in the format string?  So that later we can change it
            # to ignore unchecking if we want.
            if A['data']['checkItem']['state'] == 'complete':
                action_type += '-check'
            else:
                action_type += '-uncheck'

        elif action_type == 'updateChecklist':
            info = trello('/checklists/%s' % A['id'])
            card_info = trello('/cards/%s' % info['idCard'])
            params['card_name'] = escape(card_info['name'])
            params['card_url'] = card_info['url']
            if 'name' in A['data']['old']:
                params['old_name'] = escape(A['data']['old']['name'])
                params['new_name'] = escape(A['data']['checklist']['name'])
                action_type += '-rename'

        elif action_type in ('addChecklistToCard', 'removeChecklistFromCard'):
            list_name = trello('/cards/%s/list' % card_id)['name']
            if not card_in_lists(list_name, list_names):
                continue
            params['checklist_name'] = escape(A['data']['checklist']['name'])

        elif action_type == 'updateList':
            if not card_in_lists(A['data']['list']['name'], list_names):
                # This is kind of a weird check to do ...
                continue
            if 'name' in A['data']['old']:
                params['old_name'] = escape(A['data']['old']['name'])
                action_type += '-rename'
            else:
                # Otherwise, the update was for some other aspect of the list
                # than its name, e.g. its position (or archiving (TODO))
                action_type = 'default'

        elif action_type in ('createList', 'deleteCard'):
            # We have a message template for this action type, but there are
            # no additional parameters we need to get.
            pass

        else:
            # This is an action that we haven't written a template for yet.
            action_type = 'default'

        msg(room_id, MESSAGES[action_type] % params)

    # TODO: check that the whole LAST_ID logic is working correctly.
    LAST_ID = max(LAST_ID, int(A['id'], 16))


if __name__ == '__main__':
    while True:
        print('starting another round\n\n\n')
        for (board_id, parameters) in MONITOR:
            notify(board_id, **parameters)
        time.sleep(60)
        open(ROOT_DIR + '/last-action.id', 'w').write(str(LAST_ID))
