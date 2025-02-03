from Toolset.meta import *

class Calendar(ABC):
    def __init__(self,task='calendar'):
        super().__init__(task)
        self.apis={
            "CALENDAR": ['CALENDAR', r'', 'date'],
            "TIME": ['TIME', r'date:\s*([\w%\d\s]+),\s*day:\s*([\w%\d\s]+)', 'date'],
            "TRANSFER": ['TRANSFER', r'time:\s*([\w%\d\s]+),\s*zone:\s*([\w%\d\s]+),\s*zone:\s*([\w%\d\s]+)', 'time'],
        }

    def filter(self, output):
        a = self.extract(output)
        if a == []:
            return False
        for line in a:
            if line[0] not in self.apis:  # check API-name
                return False
            r = re.match(self.apis[line[0]][1], line[1])  # check parameter and type
            if r == None:
                return False
            else:
                print(r.groups())
        return True