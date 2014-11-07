# Sample configuration file

# You need a Trello API key. 
#
# Go here to generate an API key:
# https://trello.com/1/appKey/generate
# (the API secret is not needed).
TRELLO_API_KEY = "fill-in-as-explained-above"

# If you need trello-hipchat to access private boards,
# you need a OAuth token that authenticates an user that has read access to 
# all the boards you want to monitor.
#
# Go here, substituting the trello API key in the URL:
# https://trello.com/1/authorize?response_type=token&key=[TRELLO_API_KEY]&scope=read&expiration=never&name=Trello-Hipchat
#
# If you don't need access to private boards, set this to None.
TRELLO_TOKEN = "fill-in-as-explained-above"

# You need a HipChat API token. Go here to generate one:
# https://[YOUR_GROUP].hipchat.com/admin/api
#
# Create a new Notification token, label it "Trello", and paste it here.
#
HIPCHAT_API_KEY = "fill-in-as-explained-above"

# List here the Trello boards that you want to monitor, giving them a descriptive
# name like in the example. Just visit the boards and get the IDs from the URL. 
BOARD_MAIN = "123456789123456789123456789"
BOARD_BRAINSTORMING = "123456789123456789123456789123456789"

# List here the HipChat room IDs where you want to send notifications to.
# https://[YOUR_GROUP].hipchat.com/rooms/ids 
ROOM_STAFF = "44444"
ROOM_DESIGNERS = "55555"

# What color do you want Trello notifications to be in HipChat?
HIPCHAT_COLOR = "purple"

# This is the main configuration section. For each board, specify which lists
# you want to monitor, and which HipChat room send notifications to.
# List names are specified with wildcards, so just use "*" to monitor all the lists.
# Filters are functions that take an action dictionary and return True or False;
# HipChat notifications will be sent only for cards that pass all filters.
# For a list of possible actions to include, see
# https://trello.com/docs/api/board/index.html#get-1-boards-board-id-actions;
# to include all actions, leave out the include_actions list.
MONITOR = [
	( BOARD_MAIN,
		{
			"list_names": [ "Current", "Done*" ],
			"room_id": ROOM_STAFF,
                        "include_actions": ["commentCard",
                                            "addAttachmentToCard",
                                            "updateCard",
                                            "updateCheckItemStateOnCard"]
		}
	),
	( BOARD_BRAINSTORMING,
		{
			"list_names": [ "*" ],
			"room_id": ROOM_DESIGNERS,
                        "include_actions": ["createCard"]
		}
	),
]
