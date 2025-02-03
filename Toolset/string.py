from Toolset.meta import *

class String(ABC):
    def __init__(self,task='string'):
        super().__init__(task)
        self.apis={
            "CHANGE":["CHANGE",r'int:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*character([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)','String',
                      'CHANGE(String: s, int i, character: c) → String : change the i-th position of String `s` to character `c`. '],
            "FILTER": ['FILTER', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*feature:\s*([\w%\d\s]+)', 'String',
                       'FILTER(string: s, feature: f) → String: filter each character of the string `s` based on the feature `f`, and only keep the character match the condition. `f` should be `lower`, `upper`, `letter` or `digital` which used to filter uppercase letters, lowercase letters, numbers and English letters respectively.'],
            "LOWER": ['LOWERCASE', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'string',
                      'LOWER(string: s) → string: convert each character in the string s to lowercase.'],
            "UPPER": ['ENDSWITH', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'string',
                      'UPPER(string: s) → string: convert each character in the string s to uppercase.'],
            "JOIN": ['JOIN', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'string',
                     'JOIN(string: s1, string: s2) → string: concatenates two strings `s1` and `s2`.'],
            "INDEX": ['INDEX', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*int:\s*([\w%\d\s\-+/*]+)', 'character',
                      'INDEX(string: s, int: i) → character: get the i-th character of the string `s`.'],
            "SPLIT": ['SPLIT', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'list',
                      'SPLIT(string: s, string: sep) → list: return a list of the substrings in the string `s`, using `sep` as the separator string.'],
            "REPLACE":['REPLACE',r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*character:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*character:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'string',
                       'REPLACE(string: s, character: c1, character: c2) → string: replace each character `c1` in string `s` with character `c2`.'],
            "REMOVE": ['REMOVE', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'string',
                       'REMOVE(string: s, string: s1) → string: remove the substring `s1` in the string `s`, and get the result.'],
            "COUNT": ['COUNT', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*character:\s*([\w%\d\s]+)', 'number',
                      'COUNT(string: s, character: c) → number: get the number of character `c` in the string `s`.'],
            "SIZE": ['SIZE', r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+)', 'number',
                     'SIZE(string: s) → number: get the number of character in string `s`.'],
            "INSERT":['INSERT',r'string:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*character:\s*([\w\d\s+/*\-@#$%^&!?\\()~;\'",.]+),\s*int:\s*([\w%\d\s]+)','string',
                      'INSERT(string: s, character: c, int: i) → string: add the new character `c` in the i-th position of the string `s`.'],
            "CAL": ['CAL', r'expression:\s*([\w%\d\s+\-*/()]+)', 'float',
                    'CAL(expression: e) → float: calculate the result of expression `e`, e.g., 1+2, 1/3, 4*5 and 7-1.'],
        }

    def extract(self,s):
        """

        :param s: string, the output from chatgpt
        :return: using `re` library to extract the API  which called by chatgpt
        """
        a = re.findall(r'\[([A-Z]+)\(([()\-\w\d,.:\s%/><=#$@!^~"\';\\?*]*)\)\s*→\s*([\w%\d+\-*/]+)]',s)
        return a

    def filter(self, output):
        a = self.extract(output)
        if a == []:
            return None
        t = []
        for line in a:
            if line[0] not in self.apis:  # check API-name
                print(f'{line[0]} is not defined, {line[1]}')
                return None
            r = re.match(self.apis[line[0]][1], line[1], re.ASCII)  # check parameter and type
            if r == None:
                print(f"the parameter of {line[0]} is wrong, {line[1]}")
                return None
            for k, v in self.apis.items():
                if k in line[1]:
                    return None  
            t.append(line + (self.apis[line[0]][-1],))  
            # else:
            #     print(r.groups())
        return t
