import time

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
