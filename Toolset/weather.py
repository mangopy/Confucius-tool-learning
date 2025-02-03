from Toolset.meta import *


class Weather(ABC):
    def __init__(self, task='weather'):
        super().__init__(task)
        self.apis = {
            "CALENDAR": ['CALENDAR', r'', 'date',
                         'CALENDAR() → date:  get the date of today.'],
            "TIME": ['TIME', r'date:\s*([\w%\d\s\-]+),\s*day:\s*([\w%\d\s\-]+)', 'date',
                     "TIME(date: d, day: n) → time: get the time of `n' days before date `d` (d<0) or after date `d` (d>0)."],
            "CAL": ['CAL', r'expression:\s*([\w%\d\s+\-*/]+)', 'float',
                    'CAL(expression: e) → float: calculate the result of expression `e`, e.g., 1+2, 1/3, 4*5 and 7-1.'],
            "QUERY": ['QUERY', r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+),\s*date:\s*([\w%\d\s\-]+),\s*feature:\s*([\w%\d\s=<>]+)', 'list',
                      'QUERY(city: c, date: d1, date: d2, feature: f) → list: get the list of feature of city `c` from the date `d1` to date `d2`.'],

            "TEMPERATURE": ["TEMPERATURE", r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+)', 'temperature',
                            'TEMPERATURE(city: c, date: d) → temperature: get the temperature of the city `c` in the date of `d`.'],
            "WEATHER": ['WEATHER', r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+)', 'weather',
                        'WEATHER(city: c, date: d) →  weather: get the weather of the city `c` on the date `d`.'],
            "HUMIDITY": ['HUMIDITY', r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+)', 'humidity',
                         'HUMIDITY(city: c, date: d) → humidity: get the humidity of the city `c` in the date of  `d`.'],
            "WIND": ['WIND', r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+)', 'speed',
                     'WIND(city: c, date: d) → speed: get the wind speed of the city `c` in the date of `d`.'],
            "RAINFALL": ['RAINFALL', r'city:\s*([\w%\d\s]+),\s*date:\s*([\w%\d\s\-]+)', 'rainfall',
                         'RAINFALL(city: c, date: y) → rainfall: get the rainfall of the city `c` in the year `y`.'],

            "AVERAGE": ['AVERAGE', r'list:\s*([\w%\d\s]+)', 'value',
                        'AVERAGE(list: l) → value: get the average  of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "SUM": ['SUM', 'list:\s*([\w%\d\s]+)', 'value',
                    'SUM(list: l) → value: get the sum of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "MIN": ['MIN', r'list:\s*([\w%\d\s]+)', 'value',
                    'MIN(list: l) → value: get the minimum value of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "MAX": ['MAX', r'list:\s*([\w%\d\s]+)', 'value',
                    'MAX(list: l) → value: get the minimum value of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "VARIANCE": ['VARIANCE', r'list:\s*([\w%\d\s]+)', 'value',
                         'VARIANCE(list: l) → value: get the variance of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "MEAN": ['MEAN', r'list:\s*([\w%\d\s]+)', 'value',
                     'MEAN(list: l) → value: get the mean value of the list `l`. The element of list `l` can be `temperature`, `humidity`, `wind speed` or `rainfall`.'],
            "COUNT": ['COUNT', r'list:\s*([\w%\d\s]+),\s*feature:\s*([\w%\d\s=<>]+)', 'value',
                      'COUNT(list: l, feature: f) → number: count the number of occurrences of feature `f` in list `l`.'],
            "CORREL": ['CORREL', r'list:\s*([\w%\d\s]+),\s*list:\s*([\w%\d\s]+)', 'value',
                       'CORREL(list: x, list: y) → value: get the correlation between two list `x` and `y`.'],

            "CELSIUS": ['CELSIUS', r'fahrenheit:\s*([\w%\d\s]+)', 'celsius',
                        'CELSIUS(fahrenheit: f) → celsius: convert Fahrenheit `f` to celsius.'],
            "FAHRENHEIT": ['FAHRENHEIT', r'city:\s*([\w%\d\s]+)', 'fahrenheit',
                           'FAHRENHEIT(celsius: c) → fahrenheit: convert celsius `c` to fahrenheit.'],
        }
