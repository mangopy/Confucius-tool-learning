from Toolset.meta import *


class Persona(ABC):
    def __init__(self, task='persona'):
        super().__init__(task)
        self.apis = {
            "QUERY": ['QUERY', 'name:\s*([\w%\d\s\'",.]+)', 'dictionary',
                      'QUERY(name: n) → dictionary: query reminder information named `n`.'],
            "DELETE": ['DELETE', 'name:\s*([\w%\d\s\'",.]+)', 'bool',
                       'DELETE(name: n) → bool: delete the reminder named `n`. Returns `True ` for successful deletion, `False` otherwise.'],
            "ALTER": ['ALTER', 'name:\s*([\w%\d\s\'",.]+),\s*time:\s*([\w%\d\s:\-+*/,.\'"]+)', 'bool',
                      'ALTER(name: n, time: t) → bool: alter the time of the reminder `n` to `t`. Returns `True ` for successful modification, `False` otherwise.'],
            "SET": ['SET', 'name:\s*([\w%\d\s\'",.\-]+),\s*time:\s*([\w%\d\s:\-+*/\'",.]+)', 'bool',
                    'SET(name: n, time: t) → bool: set a reminder `n` at the time `t`. Returns `True ` for successful addition, `False` otherwise.'],
            "SCHEDULE": ['SCHEDULE', 'topic:\s*([\w%\d\s:\-\'"]+),\s*start:\s*([\w%\d\s:\-*+.,\'"]+),\s*end:\s*([\w%\d\s\-:\-*+/.,\'"]+),\s*location:\s*([\w%\d\s\-,.\';"]+),\s*attendees:\s*([\w%\d\s\(),.:\'"]+)', 'status',
                         'SCHEDULE(topic: t, start: s, end: e, location: l, attendees: a) → bool: schedule a meeting. The meeting topic is `t`, the start time is `s`, the end time is `e`， the location is `l`, and the attendees are `a`. Returns True for successful addition, False otherwise.'],
            "CANCEL": ['CANCEL', 'name:\s*([\w%\d\s,.\'"]+)', 'bool',
                       'CANCEL(name: n) → bool: cancel the meeting named `n`. Returns True for successful deletion, False otherwise.'],
            "MODIFY": ['MODIFY', 'name:\s*([\w%\d\s\'",.\-]+),\s*feature:\s*([\w%\d\s\-<>=:+/*]+)', 'information',
                       'MODIFY(name: n, feature: x) → information: modify the details of a meeting and return the information about the meeting after modification.'],
            "VIEW": ['VIEW', 'name:\s*([\w%\d\s\'",.]+)', 'information',
                     'VIEW(name: n) → information: query the information of meeting `n` and return the meeting information.'],
            "GET": ['GET', 'dictionary:\s*([\w%\d\s\'",.{}]+),\s*key:\s*([\w%\d\s\-]+)', 'value',
                    "GET(dictionary: d, key: k) → value: Get the key value of the dictionary `d`. The `d` is the meeting information or the reminder information. The `k` is `time`, `location`, or` attendees`."],
            "MUSIC": ['MUSIC', 'name:\s*([\w%\d\s:\-+*/\'",.]+)', 'String',
                      "MUSIC(name: n) → String: get the song's content called `n` and plays the music."],
            "EMAIL": ['EMAIL', 'receiver:\s*([\w%\d\s\'",.()]+),\s*subject:\s*([\w%\d\s:\-+*/\'",.()]+),\s*content:\s*([\w%\d\s:\-+*/\'",.]+)', 'String',
                      'EMAIL(receiver: x, subject: s, content: c) → String: send an email to the receiver `x` with the subject `s` and the content `c`. The return value is the primary key of the sent email.'],
        }

