#!/usr/bin/env python
from __future__ import print_function
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

from .messages import MESSAGES


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


def trello(path, api_key, token=None, **kwargs):
    """
    Make a request to the Trello API.
    """
    kwargs['key'] = api_key
    if token:
        kwargs['token'] = token

    url = 'https://api.trello.com/1' + path + '?' + urlencode(kwargs)
    req = urlopen(url)
    data = req.read().decode('utf-8')
    return json.loads(data)


def send_hipchat_message(room_id, message, api_key,
                         color='purple', mtype='html', really=True):
    """
    Send a message to HipChat.
    """
    if not really:
        print('message:', message.encode('utf-8'), '\n\n\n')
        return 

    data = {
        'from': 'Trello',
        'message': message,
        'message_format': mtype,
        'color': color,
        'room_id': room_id
    }

    data = urlencode(data).encode('utf-8')
    req = urlopen(
        'https://api.hipchat.com/v1/rooms/message?format=json&auth_token=%s'
        % api_key, data
    )
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
    Return True if name matches any of the list_names (which can contain
    some regular expression syntax (the same as what can be used in the Unix
    shell)), otherwise False.
    """
    for filt in list_names:
        if name == filt or fnmatch.fnmatch(name, filt):
            return True
    return False


def get_actions(config, last_time, board_id, include_actions=['all']):
    """
    Get the list of actions from the Trello API, for a particular board.
    Return the list of actions, the highest action ID, and the most recent
    action time.
    """
    since = to_trello_date(last_time)
    print('getting actions since', since, 'for board', board_id)
    actions = trello(
        '/boards/%s/actions' % board_id,
        filter=','.join([a[:a.index('-')] if '-' in a else a
                         for a in include_actions]),
        since=since,
        api_key=config.TRELLO_API_KEY,
        token=config.TRELLO_TOKEN
    )

    # Ignore actions older than last_time
    actions = [A for A in actions if from_trello_date(A['date']) > last_time]

    # Compute the most recent time and action ID
    new_last_time = max([from_trello_date(A['date']) for A in actions] +
                        [last_time])

    return (actions, new_last_time)


def notify(config, actions, board_id, room_id, list_names,
           include_actions=['all'], filters=[], debug=False):
    """
    Given a list of actions, report all of the relevant ones to the HipChat
    room.
    """
    # Iterate over the actions, in reverse order because of chronology.
    for A in reversed(actions):

        if debug:
            print(A, '\n\n\n')

        # If this doesn't pass the filters, ignore it.
        if not all(f(A) for f in filters):
            continue

        action_type = A['type']

        params = {'author': escape(A['memberCreator']['fullName']),
                  'action_type': action_type}

        # Basic info for applicable card/list/checklist/board

        if 'card' in A['data'] and action_type != 'deleteCard':
            card_id = A['data']['card']['id']
            params['card_url'] = ('https://trello.com/c/%s/' % card_id)
            params['card_name'] = escape(A['data']['card']['name'])

        if 'list' in A['data']:
            params['list_name'] = escape(A['data']['list']['name'])

        if 'checklist' in A['data']:
            params['checklist_name'] = escape(A['data']['checklist']['name'])
            if action_type != 'removeChecklistFromCard':
                # get card info
                info = trello(
                    '/checklists/%s' % A['data']['checklist']['id'],
                    api_key=config.TRELLO_API_KEY,
                    token=config.TRELLO_TOKEN
                )
                card_id = info['idCard']
                card_info = trello(
                    '/cards/%s' % card_id,
                    api_key=config.TRELLO_API_KEY,
                    token=config.TRELLO_TOKEN
                )
                params['card_url'] = card_info['url']
                params['card_name'] = escape(card_info['name'])
                # get list info
                list_info = trello(
                    '/cards/%s/list' % card_id,
                    api_key=config.TRELLO_API_KEY,
                    token=config.TRELLO_TOKEN
                )
                params['list_name'] = escape(list_info['name'])

        if 'board' in A['data']:
            params['board_name'] = escape(A['data']['board']['name'])
            params['board_url'] = 'https://trello.com/b/%s/' % board_id

        # If this action is in a list that's not relevant, ignore it
        if 'list_name' in params and \
           not card_in_lists(params['list_name'], list_names):
            continue

        # Construct message parameters for specific action types

        if action_type == 'commentCard':
            params['text'] = trunc(escape(' '.join(A['data']['text'].split())))

        elif action_type in ('addMemberToCard', 'removeMemberFromCard'):
            params['member'] = A['member']['fullName']

        elif action_type == 'addAttachmentToCard':
            params['attachment_name'] = escape(A['data']['attachment']['name'])
            params['attachment_url'] = A['data']['attachment']['url']
            # TODO: send the attachment if it's an image?

        elif action_type in ('updateCard', 'updateList', 'updateChecklist') \
             and 'name' in A['data']['old']:
            # Rename a card, list, or checklist
            params['old_name'] = escape(A['data']['old']['name'])
            action_type += '-rename'

        elif action_type in ('updateCard', 'updateList') \
             and 'closed' in A['data']['old']:
            # Archive a card or list
            if A['data']['old']['closed']:
                action_type += '-unarchive'
            else:
                action_type += '-archive'

        elif action_type == 'updateCard':
            if 'idList' in A['data']['old']:
                # Move between lists
                old_list_name = A['data']['listBefore']['name']
                new_list_name = A['data']['listAfter']['name']

                if not (card_in_lists(old_list_name, list_names) or
                        card_in_lists(new_list_name, list_names)):
                    continue
                params['old_list'] = escape(old_list_name)
                params['new_list'] = escape(new_list_name)
                action_type += '-move'
            elif 'desc' in A['data']['old']:
                action_type += '-description'
                params['description'] = trunc(escape(
                    ' '.join(A['data']['card']['desc'].split())))
            else:
                # Some other type of card update
                params['attribute'] = list(A['data']['old'])[0]

        elif action_type in ('moveCardFromBoard', 'moveListFromBoard'):
            params['to_board_url'] = ('https://trello.com/b/%s/' %
                                      A['data']['boardTarget']['id'])
            params['to_board_name'] = escape(A['data']['boardTarget']['name'])

        elif action_type == ('moveCardToBoard', 'moveListToBoard'):
            params['from_board_url'] = ('https://trello.com/b/%s/' %
                                        A['data']['boardSource']['id'])
            params['from_board_name'] = escape(A['data']['boardSource']['name'])

        elif action_type == 'updateCheckItemStateOnCard':
            params['item_name'] = escape(A['data']['checkItem']['name'])
            if A['data']['checkItem']['state'] == 'complete':
                action_type += '-check'
            else:
                action_type += '-uncheck'

        elif action_type == 'updateList':
            params['attribute'] = list(A['data']['old'])[0]

        elif action_type in ('createCard', 'deleteCard', 'createList',
                             'addChecklistToCard', 'removeChecklistFromCard'):
            # We have a message template for this action type, but there are
            # no additional parameters we need to get.
            pass

        else:
            # This is an action that we haven't written a template for yet.
            action_type = 'default'

        # Check the action type (at the end so it can check subtype)
        if (include_actions != ['all'] and
            action_type != 'default' and
            action_type not in include_actions):
            continue

        send_hipchat_message(
            room_id, MESSAGES[action_type] % params, config.HIPCHAT_API_KEY,
            color=config.HIPCHAT_COLOR, really=(not debug)
        )
