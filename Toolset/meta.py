import re

class ABC(object):
    def __init__(self,task,apis=None):
        self.task=task
        self.apis=apis

    def filter(self, output):
        a = self.extract(output)

        if output.count('→') != len(a):
            return None
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
                    print(f'插件之间存在嵌套：{line[0]} {line[1]}')
                    return None  
            t.append(line+(self.apis[line[0]][-1],)) 
        return t

    def extract(self,s):
        """

        :param s: String, the output from chatgpt
        :return: using `re` library to extract the API  which called by chatgpt
        """
        a = re.findall(r'\[([A-Z]+)\(([\-\w\d,.:\s%/><=*+"\'?#]*)\)\s*→\s*([\w%\d+\-*/"\'?,.:\s#()><=–]+)]',s)
        return a
