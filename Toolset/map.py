from Toolset.meta import *


class Map(ABC):
    def __init__(self, task='map'):
        super().__init__(task)
        # the api and corresponding pattern used for `re` python library
        self.apis = {
            "PATH": ['PATH', r'place:\s*([\w%\d\s]+),\s*place:\s*([\w%\d\s]+)', 'list',
                     'PATH(place: p1, place: p2) → list: get the list of path from place `p1` to place `p2`.'],
            "DISTANCE": ['DISTANCE', r'place:\s*([\w%\d\s]+),\s*place:\s*([\w%\d\s]+)', 'distance',
                         'DISTANCE(place: p1, place: p2) → distance: get the distance from place `p1` to place `p2`.'],
            "SORT": ['SORT', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                     'SORT(list: l, feature: f) → list: sort the list of path `l` based on the feature `f`, such as the cost, distance and time.'],
            "FILTER": ['FILTER', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                       'FILTER(list: l, feature: f) → list: filter the list of path `l` based on feature `f` and keep only the paths that match the feature(e.g., cost, distance and time).'],
            "AVERAGE": ['AVERAGE', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                        'AVERAGE(list: l, feature: f) → path: get the average of the path list `l` based on the feature f (e.g., cost, distance and time).'],
            "MIN": ['MIN', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                    'MIN(list: l, feature: f) → path: get path from the path list `l` which has the the minimum feature.'],
            "MAX": ['MAX', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                    'MAX(list: l, feature: f) → path: get path from the path list `l` which has the the maximum feature.'],
            "INDEX": ['INDEX', r'list:\s*([\w%\d\s]+),\s*int:\s*([\-\d]+)', 'path',
                      'INDEX(list: l, int: i) → path: get the i-th path from the list of path.'],
            "CAL": ['CAL', r'expression:\s*([\w%\d\s\-/*+]+)', 'float',
                    'CAL(expression: e)->float: calculate the result of expression `e`, e.g. 1+2, 1/3, 4*5 and 7-1.  The expressions `e` can be about time, money or distance'],
            "TIME": ['TIME', r'path:\s*([\w%\d\s]+)', 'time',
                     'TIME(path: p) → time: get the time of the path `p`.'],
            "BOOK": ['BOOK', r'path:\s*([\w%\d\s]+)', 'ticket',
                     'BOOK(path: p) → ticket: book a ticket of the path `p`.'],
            "COST": ['COST', r'path:\s*([\w%\d\s]+)', 'cost',
                     'COST(path: p) → cost: get the cost of path `p`.'],
            "REFUND": ['REFUND', r'ticket:\s*([\w%\d\s]+)', 'cost',
                       'REFUND(ticket: t) → money: return the ticket `t` and get the money.'],
            "RESCHEDULE": ['RESCHEDULE', r'ticket:\s*([\w%\d\s]+),\s*path:\s*([\w\d%\s]+)', 'ticket',
                           'RESCHEDULE(ticket: t, path: p) → ticket: reschedule the ticket to a new path `p` and get the new ticket.'],
        }
