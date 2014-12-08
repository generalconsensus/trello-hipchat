from __future__ import print_function
import os
import sys
import time
import json
import logging
import logging.config
from collections import defaultdict
from argparse import ArgumentParser

from . import get_actions, notify

# The error you get for a nonexistent file is different on py2 vs py3.
if sys.version_info[0] > 2:
    FileNotFound = FileNotFoundError
else:
    FileNotFound = IOError

def run_forever():
    """
    Command-line interface.
    Every minute, send all the notifications for all the boards.
    """
        
    # Parse command-line args
    parser = ArgumentParser()
    parser.add_argument('config_file', type=str,
                        help='Python file to load configuration from')
    parser.add_argument('-d', type=str, dest='directory', default='.',
                        help='Directory in which to save/read state')
    parser.add_argument('-i', type=int, dest='interval', default=60,
                        help='Number of seconds to sleep between rounds')
    parser.add_argument('--debug', action='store_true',
                        help=('Print actions and messages, and don\'t actually'
                              ' send to HipChat'))
    args = parser.parse_args()

    # Set up logging
    # logger = logging.getLogger(__name__)
    # logging.config.fileConfig(('logging_debug.cfg'
    #                            if args.debug
    #                            else 'logging.cfg'),
    #                           disable_existing_loggers=False)
    
    # Load config file
    try:
        if sys.version_info[0] > 2:
            import importlib
            config = importlib.machinery.SourceFileLoader(
                'config', args.config_file).load_module()
        else:
            import imp
            with open(args.config_file) as f:
                config = imp.load_module('config', f, args.config_file,
                                         ('.py', 'r', imp.PY_SOURCE))

    except (FileNotFound, SyntaxError):
        sys.exit(1)

    if not config.MONITOR:
        sys.exit(2)

    interval = max(0, args.interval)

    state_file = os.path.join(args.directory, 'last-actions.json')
    # Don't check back in time more than 20 minutes ago.
    a_while_ago = time.time() - 20*60
    last_action_times = defaultdict(lambda: a_while_ago)
    try:
        last_action_times.update(json.load(open(state_file)))
    except (FileNotFound, ValueError):
        print "Warning: no saved state found."
        #logger.warning('Warning: no saved state found.')

    while True:
        # First get all the actions, to avoid doing it multiple times for the
        # same board.
        new_actions = {}
        for parameters in config.MONITOR:
            board_id = parameters['board_id']
            if board_id not in new_actions:
                (actions, new_last_time) = get_actions(
                    config, last_action_times[board_id], board_id)
                new_actions[board_id] = actions
                last_action_times[board_id] = new_last_time

        # Then send all the HipChat notifications.
        for parameters in config.MONITOR:
            board_id = parameters['board_id']
            notify(config, new_actions[board_id], debug=args.debug,
                   **parameters)

        # Save state to a file.
        with open(state_file, 'w') as f:
            json.dump(last_action_times, f)

        time.sleep(interval)
