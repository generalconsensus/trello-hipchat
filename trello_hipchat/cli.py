from __future__ import print_function
import os
import sys
import time
from argparse import ArgumentParser
from . import notify


# TODO: should this come from a command-line argument?
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
try:
    LAST_ID = int(open(ROOT_DIR + '/last-action.id').read())
except IOError:
    LAST_ID = 0


def run_forever():
    """
    Command-line interface.
    Every minute, send all the notifications for all the boards.
    """
    global LAST_ID

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

    interval = max(0, args.interval)
    while True:
        print('starting another round\n\n\n')
        for parameters in config.MONITOR:
            LAST_ID = notify(config, LAST_ID, **parameters)
        time.sleep(interval)
        open(ROOT_DIR + '/last-action.id', 'w').write(str(LAST_ID))
