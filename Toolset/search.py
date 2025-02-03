from Toolset.meta import *

class Search(ABC):

    def __init__(self,task='search'):
        super(Search, self).__init__(task)
        self.apis={
            "SEARCH":["SEARCH",r'\s*([\w\d\s,?.+\-*/])','answer',
                      'SEARCH(query: q) → answer: access the external documents to get the answer of the input query `q`. And the answer is a phrase']
        }