from Toolset.meta import *

class Medical(ABC):
    def __init__(self,task='medical'):
        super().__init__(task)
        self.apis = {
            "SEARCH": ['SEARCH', r'symptom:\s*([\w%\d\s]+)', 'list',
                       'SEARCH(symptom: s) → list: search for a list of disease names based on the given symptom `s`.'
                       ],

            "MEDICAL": ['MEDICAL', r'disease:\s*([\w%\d\s]+)', 'list',
                        'MEDICAL(disease: d) → list: get the list of medicine to cure the disease `d`.'
                        ],

            "ROUTE": ['ROUTE', r'symptom:\s*([\w%\d\s]+)', 'doctor',
                     'ROUTE(symptom: s) → doctor: match a suitable doctor according to the symptoms `s`.',
                      ],

            "APPOINTMENT": ['APPOINTMENT', r'user:\s*([\w%\d\s"\']+),\s*doctor:\s*([\w%\d\s=<>]+)', 'date',
                       'APPOINTMENT(user: u, doctor: t) → date: make an appointment with doctor `t`.'],
            "SYMPTOM": ['SYMPTOM', r'disease:\s*([\w%\d\s]+)', 'symptom',
                        'SYMPTOM (disease: d) → symptom: search the symptom of the given disease `d`.'],
            "COST": ['COST', r'medical:\s*([\w%\d\s]+)', 'money',
                    'COST(medical: m) → money: get the cost of the medical `m`.'],
            "REMAINDER": ['REMAINDER', r'date:\s*([\w%\d\s]+),\s*record:\s*([\w%\d\s=<>]+)', 'bool',
                    'REMAINDER(date: d, record: r) → bool: set a record `r` on the memo on a date `d`.'],
            "INDEX": ['INDEX', r'list:\s*([\w%\d\s]+),\s*int:\s*([\-\d]+)', 'item',
                      'INDEX(list: l, int: i) → item: get the i-th item of the list `l`.'],
            "CALENDAR": ['CALENDAR', r'expression:\s*([\w%\d\s+\-/*]+)', 'float',
                    'CALENDAR() → date: get the date of today.'],
            "TIME": ['TIME', r'date:\s*([\w%\d\s]+),\s*day:([\w%\d\s+\-]+)', 'time',
                     'TIME(date: d, day: n) → date: get the time of `n` days before date `d` (d<0) or after date `d` (d>0).'],
            "SORT": ['SORT', r'list:\s*([\w%\d\s]+),\s*feature:([\w%\d\s]+)', 'list',
                     'SORT(list: l, feature: f) → list: sort the list `l` based on the feature `f`.'],
        }
