# This file contains a mapping from Trello action types to format strings for
# the corresponding message to be sent to HipChat.
# Some of them are not actual Trello actions, they're subsets (delimited by a
# hyphen).  For example, updateCheckItemStateOnCard-uncheck.

MESSAGES = {
    'addAttachmentToCard': "%(author)s added an attachment to card <a href=\"%(card_url)s\">%(card_name)s</a>: <a href=\"%(attachment_url)s\">%(attachment_name)s</a>.",

    'addChecklistToCard': "%(author)s added checklist \"%(checklist_name)s\" to card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'addMemberToCard': "%(author)s added %(member)s to card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'commentCard': "%(author)s commented on card <a href=\"%(card_url)s\">%(card_name)s</a>: %(text)s",

    'createCard': "%(author)s created card <a href=\"%(card_url)s\">%(card_name)s</a> in list \"%(list_name)s\".",

    'createList': "%(author)s created list \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    # Trello doesn't tell you the name of the card when you delete it.
    'deleteCard': "%(author)s deleted a card from list \"%(list_name)s\".",

    'moveCardFromBoard': "%(author)s moved card <a href=\"%(card_url)s\">%(card_name)s</a> from board <a href=\"%(board_url)s\">%(board_name)s</a> to board <a href=\"%(to_board_url)s\">%(to_board_name)s</a>.",

    'moveCardToBoard': "%(author)s moved card <a href=\"%(card_url)s\">%(card_name)s</a> from board <a href=\"%(from_board_url)s\">%(from_board_name)s</a> to board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'moveListFromBoard': "%(author)s moved list \"%(list_name)s\" from board <a href=\"%(board_url)s\">%(board_name)s</a> to board <a href=\"%(to_board_url)s\">%(to_board_name)s</a>.",

    'moveListToBoard': "%(author)s moved list \"%(list_name)s\" from board <a href=\"%(from_board_url)s\">%(from_board_name)s</a> to board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'removeChecklistFromCard': "%(author)s removed checklist \"%(checklist_name)s\" from card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'removeMemberFromCard': "%(author)s removed %(member)s from card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateCard': "%(author)s updated \"%(attribute)s\" of card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateCard-archive': "%(author)s archived card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateCard-description': "%(author)s updated description on card <a href=\"%(card_url)s\">%(card_name)s</a>: %(description)s",

    'updateCard-move': "%(author)s moved card <a href=\"%(card_url)s\">%(card_name)s</a> from list \"%(old_list)s\" to list \"%(new_list)s\".",

    'updateCard-rename': "%(author)s renamed card <a href=\"%(card_url)s\">%(card_name)s</a> from \"%(old_name)s\".",

    'updateCard-unarchive': "%(author)s unarchived card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateCheckItemStateOnCard-check': "%(author)s completed checklist item \"%(item_name)s\" in card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateCheckItemStateOnCard-uncheck': "%(author)s unchecked checklist item \"%(item_name)s\" in card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateChecklist': "%(author)s updated \"%(attribute)s\" of checklist on card <a href=\"%(card_url)s\">%(card_name)s</a>.",

    'updateChecklist-rename': "%(author)s renamed checklist on card <a href=\"%(card_url)s\">%(card_name)s</a> from \"%(old_name)s\" to \"%(checklist_name)s\".",

    'updateList': "%(author)s updated \"%(attribute)s\" of list \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'updateList-archive': "%(author)s archived list \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'updateList-rename': "%(author)s renamed list \"%(old_name)s\" to \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'updateList-unarchive': "%(author)s unarchived list \"%(list_name)s\" on board <a href=\"%(board_url)s\">%(board_name)s</a>.",

    'default': "%(author)s did %(action_type)s.",
}
