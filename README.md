Integrate Trello and HipChat
============================
Send Trello activity logs to HipChat rooms.

This program will monitor multiple Trello boards/lists and send notifications
to multiple HipChat rooms. You can monitor a whole board, or just a specific
subset of lists within it.  You can monitor particular actions or all types of
actions.

How to install
==============
 
  * Run `python setup.py install`.
  * Copy the sample configuration from `trello_hipchat_config_sample.py` to 
    some other file.
  * Go through the configuration file, read the comments and follow all the
    instructions to get all the required API keys, tokens, IDs, etc.
  * Run the program using the `trello-hipchat` command.