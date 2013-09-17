# This file contains a mapping from Trello action types to format strings for
# the corresponding message to be sent to HipChat.
# Some of them are not actual Trello actions, they're subsets (delimited by a
# hyphen).  For example, updateCheckItemStateOnCard-uncheck.

MESSAGES = {
    'createCard': "%(author)s created card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'commentCard': "%(author)s commented on card <a href=\"%(card_url)s\">%(card_name)s</a>: %(text)s",

    'addAttachmentToCard': "%(author)s added an attachment to card <a href=\"%(card_url)s\">%(card_name)s</a>: <a href=\"%(attachment_url)s\">%(attachment_name)s</a>",

    'updateCard': "%(author)s moved card <a href=\"%(card_url)s\">%(card_name)s</a> from list \"%(old_list)s\" to list \"%(new_list)s\"",

    'updateCheckItemStateOnCard-check': "%(author)s completed checklist item \"%(item_name)s\" in card <a href=\"%(card_url)s\">%(card_name)s</a>",

    'updateCheckItemStateOnCard-uncheck': "%(author)s unchecked checklist item \"%(item_name)s\" in card <a href=\"%(card_url)s\">%(card_name)s</a>",

    'createList': "%(author)s created list \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>"
    }
