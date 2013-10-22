import time
import fnmatch

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
    return time.mktime(time.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ'))


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
