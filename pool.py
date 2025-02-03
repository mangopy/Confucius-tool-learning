from collections import defaultdict
from Toolset.map import Map
from Toolset.weather import Weather
from Toolset.calendar import Calendar
from Toolset.gsm8k import Math
from Toolset.medical import Medical
from Toolset.search import Search
from Toolset.ecommerce import Ecommerce
from Toolset.math import Geometry
from Toolset.database import Database
from Toolset.string import String
from Toolset.persona import Persona

tmp=[Map(),
     Weather(),
     Calendar(),
     Math(),
     Medical(),
     Search(),
     Ecommerce(),
     String(),
     Geometry(),
     Database(),
     Persona()]

api_pool=defaultdict(list)
task_api=[]
task_api_pool=defaultdict(dict)
task_pool=[]
for line in tmp:
     task_pool.append(line.task)
     for k,v in line.apis.items():
          api_pool[line.task].append(v[-1])
          task_api_pool[line.task][k]=v[-1]
          task_api.append(v[0])

# test
# print(task_pool)
# print(api_pool)