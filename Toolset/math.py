from Toolset.meta import *

class Geometry(ABC):
    def __init__(self,task='geometry'):
        super().__init__(task)
        self.apis={
            "CIRCLE":['CIRCLE',r'radius:\s*([\w\d\s%+\-*/]+)','float',
                      "CIRCLE(radius: r) → float: calculate the area of the circle, where the `r` is the circle's radius."],
            "SQUARE":['SQUARE',r'length:\s*([\w\d\s%+\-*/]+)','float',
                      'SQUARE(length: x) → float: calculate the area of the square, where the `x` is the side length.'],
            "RECTANGLE":['RECTANGLE',r'length:\s*([\w\d\s%+\-*/]+),\s*width:\s*([\w\d\s%+\-*/]+)','float',
                      "RECTANGLE(length: a, width: b) → float: calculate the area of the rectangle, where the side length is `a' and `b`."],
            "TRIANGLE":['TRIANGLE',r'length:\s*([\w\d\s%+\-*/]+),\s*height:\s*([\w\d\s%+\-*/]+)','area',
                      'TRIANGLE(length: l, height: h) → area: calculate the area of the triangle, where the `l` is the length and `h` is the corresponding height.'],
            "EQUATOR":['EQUATOR',r'expression:\s*([\w\d\s%+\-*/]+),\s*expression:\s*([\w\d\s%+\-*/]+)','double',
                  'EQUATOR(expression: left, expression right) → double: solve the equator and get the value of the variable. The `left` and `right` are calculation expressions containing the variable `x`.'],
            "SQRT":['SQRT',r'expression:\s*([\w\d\s%+\-*/]+)','double',
                  'SQRT(expression: e) → double: get the square root of expression `e`. For example, SQRT(4)=2 and SQRT(16)=4.'],
            "CAL":["CAL",r'expression:\s*([\w\d\s%+\-*/]+)',"float",
                'CAL(expression: e) → float: calculate the expression `e` result, e.g., 1+2, 1/3, 4*5, and 7-1.']
        }

    def extract(self,s):
        """

        :param s: String, the output from chatgpt
        :return: using `re` library to extract the API  which called by chatgpt
        """
        a = re.findall(r'\[([A-Z]+)\(([\-\w\d,.:\s%/><=*+"\'?#]*)\)\s*→\s*([\w%\d+\-*/"\'?,.:\s#()><=–]+)]',s)
        return a
