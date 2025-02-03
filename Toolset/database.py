from Toolset.meta import *


class Database(ABC):
    def __init__(self, task='database'):
        super().__init__(task)
        # the api and corresponding pattern used for `re` python library
        self.apis = {
            "TABLE": ['TABLE', r'name:\s*([\w%\d\s\'"]+)', 'table',
                     "TABLE(name: n) → table: get the table named 'n'.",
                      ],
            "CREATE": ['CREATE', r'name:\s*([\w%\d\s\'"]+),\s*list([\w%\d\s\'"]+)', 'table',
                     "CREATE(name: n, list: c) → table: create a table named `n`. List `c` contains the name of each column of `t`."],
            "INSERT": ['INSERT', r'table:\s*([\w%\d\s\'"]+),\s*item:\s*([\w%\d\s\'"{}()]+)', 'table',
                     "INSERT(table: t, item: x) → table: insert the item `x` into the table `t`. Return `True` if inserted successfully, else `False`."],
            "REMOVE": ['REMOVE', r'table:\s*([\w%\d\s\'"]+),\s*feature:\s*([\w%\d\s\'"]+)', 'table',
                       "REMOVE(table: t, feature: x) → table: delete the item `x` from the table `t`. It returns `True` if inserted successfully, else `False`."],
            "UPDATE": ['UPDATE', r'table:\s*([\w%\d\s]+),\s*feature:\s*([\w\d%\s]+),\s*strategy:\s*([\w\d%\s+\-/*=><]+)', 'index',
                        "UPDATE(table: t, feature: f, strategy: s) → table: update each item of the table `t` which matches the feature `f` based on the strategy `s`."],
            "COUNT": ['COUNT', r'table:\s*([\w%\d\s:\-+*/]+)', 'int',
                     "COUNT(table: t) → int: get the size of the table `t`."],
            "SELECT": ['FIND', r'table:\s*([\w%\d\s]+),\s*condition:\s*([\w\d%\s]+)', 'table',
                     "SELECT(table: t, condition: c) → table: get the sub-table of the item from the table `t` which matches the condition `c`. The condition refers to the column of the table `t`."],
            "DESCEND": ['DESCEND', r'table:\s*([\w%\d\s]+),\s*feature:\s*([\w\d%\s]+)', 'table',
                     "DESCEND(table: t, feature: f) → list: sort the table `t` in descending order based on the feature `f`, which indicates the column name of the table."],
            "ASCEND": ['ASCEND', r'table:\s*([\w%\d\s]+),\s*feature:\s*([\w\d%\s]+)', 'table',
                       "ASCEND(table: t, feature: f) → list: sort the table `t` in ascending order based on the feature `f`, which indicates the column name of the table."],
            "INTERSECTION":['INTERSECTION', r'table:\s*([\w%\d\s]+),\s*table:\s*([\w\d%\s]+)', 'table',
                        "INTERSECTION(table: a, table: b) → table: get the intersection of table `a' and table `b`." ],
            "UNION": ['UNION', r'table:\s*([\w%\d\s]+),\s*table:\s*([\w\d%\s]+)', 'table',
                       "UNION(table: a, table: b) → table: get the union of table `a' and table `b`."],
            "SUM": ['SUM', r'table:\s*([\w%\d\s]+),\s*column:\s*([\w\d%\s]+)', 'float',
                      "SUM(table: t, column: c) → float: get the total sum value of the column `c` in table `t`."],
            "AVG":["AVG",r"table:\s*([\w%\d\s]+),\s*column:\s*([\w\d%\s]+)","float",
                'AVG(table: t, cloumn: col) → float: get the average value of the column `col` in table `t`'],
            "GET": ['GET', r'item:\s*([\w%\d\s]+),\s*attribute:\s*([\w\d%\s=<>\-*/]+)', 'table',
                    "GET(item: x, attribute: a) → value: get the attribute `a` of the item `x`. The attribute refers to the key of the item `x`."],
            "INDEX": ['INDEX', r'table:\s*([\w%\d\s]+),\s*number:\s*([\w\d%\s]+)', 'table',
                    "INDEX(table: t, int: i) → item: get the i-th item from the table `t`."],
            "FIND":['FIND',r'table:\s*([\w\s\d]+),\s*feature:\s*([\w\d\s+\-*/=<>]+)','index'
                'FIND(table: t, feature: x) → index: get the index of the first item which matches the feature `f` in the table `t`. The feature refers to the column of the table `t`.']
        }

    def extract(self,s):
        """

        :param s: String, the output from chatgpt
        :return: using `re` library to extract the API  which called by chatgpt
        """
        a = re.findall(r'\[([A-Z]+)\(([\-\w\d,.:\s%/><={}]*)\)\s*→\s*([\w%\d]+)]',s)
        return a

