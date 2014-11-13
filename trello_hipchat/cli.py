from __future__ import print_function
import os
import sys
import time
import json
from collections import defaultdict
from argparse import ArgumentParser
from . import get_actions, notify


def run_forever():
    """
    Command-line interface.
    Every minute, send all the notifications for all the boards.
    """
    # Parse command-line args
    parser = ArgumentParser()
    parser.add_argument('config_file', type=str,
                        help='Python file to load configuration from')
    parser.add_argument('-i', type=int, dest='interval', default=60,
                        help='Number of seconds to sleep between rounds')
    args = parser.parse_args()

    # Load config file
    try:
        if sys.version_info.major > 2:
            import importlib
            config = importlib.machinery.SourceFileLoader(
                'config', args.config_file).load_module()
        else:
            import imp
            with open(args.config_file) as f:
                config = imp.load_module('config', f, args.config_file,
                                         ('.py', 'r', imp.PY_SOURCE))

    except (
        IOError,            # File doesn't exist (py2)
        FileNotFoundError,  # File doesn't exist (py3)
        SyntaxError         # File isn't valid Python
    ):
        print('Unable to import file', args.config_file)
        sys.exit(1)

    if not config.MONITOR:
        print('Nothing to monitor!')
        sys.exit(0)

    interval = max(0, args.interval)

    # TODO: should this come from a command-line argument?
    root_dir = os.path.abspath(os.path.dirname(__file__))
    try:
        last_action_times = json.load(open(root_dir + '/last-actions.json'))
    except (IOError, FileNotFoundError, ValueError):
        # Don't check back in time more than 20 minutes ago.
        a_while_ago = time.time() - 20*60
        last_action_times = defaultdict(lambda: a_while_ago)

    while True:
        print('starting another round\n\n\n')

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
            notify(config, new_actions[board_id], **parameters)

        # Save state to a file.
        with open(root_dir + '/last-actions.json', 'w') as f:
            json.dump(last_action_times, f)

        time.sleep(interval)
