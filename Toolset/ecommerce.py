from Toolset.meta import *

class Ecommerce(ABC):
    def __init__(self, task='e-commerce'):
        super().__init__(task)
        self.apis = {
            "BUY": ['BUY', r'user:\s*([\w%\d\s]+),\s*item:\s*([\w%\d\s]+)', 'item',
                    'BUY(user:u, item: x) → item: buy the item `x` for user `u`.'],
            "TRACK": ['TRACK', r'item:\s*([\w%\d\s]+)', 'date',
                      'TRACK(item: x) → date: get the delivery date of the item `x`.'],
            "FIND": ['FIND', r'name:\s*([\w%\d\s]+)', 'list',
                     'FIND(name: n) → list: search the item named `n` and get the relevant item list.'],
            "SORT": ['SORT', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=]+)', 'list',
                     'SORT(list: l, feature: f) → list: sort the item list `l` based on the feature `f`, which can be `cost`, `date` or `distance`.'],
            "RETURN": ['RETURN', r'item:\s*([\w%\d\s]+)', 'money',
                       'RETURN(item: i) → money: return the item `x` and refund the money.'],
            "MIN": ['MIN', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'item',
                    'MIN(list: l, feature: f) → item: get the item from the item list `l` which has the minimum feature `f`. The feature is `cost`, `date` or `distance`.'],
            "MAX": ['MAX', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'item',
                    'MAX(list: l, feature: f) → item: get the item from the item list `l` which has the maximum feature `f`. The feature is `cost`, `date` or `distance`.'],
            "CHANGE": ['CHANGE', r'item:\s*([\w%\d\s]+),\s*style:\s*([\w%\d\s=<>\-*+()]+)', 'item',
                       'CHANGE(item: x,  style: s) → item: change the item `x` with style `s`, where the `s` refers to the color, size, thickness, etc.'],
            "HISTORY": ['CHANGE', r'user:\s*([\w%\d\s]+)', 'item',
                        'HISTORY(user: u) → list: get all items purchased by users `u`.'],
            "INDEX": ["INDEX", r'list:\s*([\w%\d\s]+),\s*int:\s*([\w%\d\s]+)', "item",
                      'INDEX(list: l, int: i) → path: get the i-th path from the list of path.'],
            "CAL": ['CAL', r'expression:\s*([\w%\d\s*\-+/=<>]+)', 'float',
                    'CAL(expression: e) → float: calculate the result of expression `e`, e.g., 1+2, 1/3, 4*5 and 7-1.'],
            "FILTER": ['FILTER', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>*\-/+]+)', 'list',
                       'FILTER(list: l, feature: f) → list: filter the item from the item list `l`. And only item which matches the feature `f` will be kept.'],
            "SUM": ['SUM', r'list:\s*([\w%\d\s]+)', 'value',
                    'SUM(list: l): →  float: calculate the sum cost of all the item in list `l`.'],
            "TOPK": ['TOPK', r'list:\s*([\w%\d\s]+),\s*int:\s*([\w%\d\s]+)', 'list',
                     'TOPK(list: l, int: r) → list: get the top `r` item from the list.'],
            "CALENDAR": ["CALENDAR", r'', 'date',
                         'CALENDAR() → date:  get the date of today.'],
            "COST": ['COST', r'item:\s*([\w%\d\s]+)', 'money',
                     'COST(item: x) → money :compute the price of the item x.'],
            "TIME": ['TIME', r'date:\s*([\w%\d\s]+),\s*day:\s*([-\d+\s]+)','date',
                     'TIME(date: d, day: n) → date: get the time of `n` days before date `d` (d<0) or after date `d` (d>0).']
        }
