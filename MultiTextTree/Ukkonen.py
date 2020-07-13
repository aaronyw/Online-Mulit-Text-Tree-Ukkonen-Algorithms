from MultiTextTree.Radix import *


class Ukkonen(Radix):
    def __init__(self, debug=False, end='$'):
        super().__init__(end)
        self.debug = debug
        self.__anode = 0  # active nodes list
        self.__aedge = 0  # active edge
        self.__alen = 0  # active length
        self.__ext = 0  # extent active range pointer
        self.__reminder = 0  # reminder
        self.__prenode = (0, 0)

    def push(self, i):
        f = True
        while i < len(self.text):
            self.debuginfo('+ + + + + + CHR {} BEGIN + + + + + + +'.format(i))
            f, i = self.__ukkonen_constructor(i, f)
            self.debuginfo('+ + + + + + CHR {} END + + + + + + +'.format(i), min(self.__ext + 1, len(self.text)))

    def __ukkonen_constructor(self, i, flag=False):

        def dive(i):
            self.__aedge = self.__aedge if self.__aedge else i
            self.debuginfo('DIVE {} \'{}\':'.format(i, self.text[i]))
            if self.text[self.__aedge] in self.nodes[self.__anode].edges:
                aedge = self.nodes[self.__anode].edges[self.text[self.__aedge]]
                if aedge.des and self.__alen >= aedge.end - aedge.start:  # change active node
                    self.__anode = aedge.des
                    self.__alen -= aedge.end - aedge.start
                    self.__aedge = i - self.__alen
                    return dive(i)
                if self.text[i] == self.text[aedge.start + self.__alen]:  # walk down the edge
                    self.__alen += 1
                    self.__reminder += 1
                    return True
            return False

        def apply_suffix_rules():  # Source: https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
            if n:
                if self.__prenode[1] == self.__ext and n not in self.nodes[self.__prenode[0]].children()[0]:  # RULE No.2
                    self.nodes[self.__prenode[0]].suffixlink = n
                    self.debuginfo('RULE 2: SUFFIX LINKED from node {} to {}'.format(self.__prenode[0], n))
                self.__prenode = (n, self.__ext)
            _d = self.nodes[self.__anode].suffixlink
            if self.__anode:  # RULE No.3
                self.__anode = _d
                if not _d and self.__reminder:
                    return True  # need to do a search from root
                else:
                    self.debuginfo('RULE 3: SUFFIX LINK followed to node {}'.format(_d))
            else:  # RULE No.1
                self.__aedge = min(len(self.text) - 1, self.__aedge + 1)
                self.__alen = max(self.__alen - 1, 0)
            return False

        n = 0
        self.__ext = max(self.__ext, i)
        if flag:  # need to do a search
            _r = self.search(self.text[i:self.__ext])
            self.debuginfo('NEED to do a search from \'{}\': {}'.format(self.text[i:self.__ext], _r))
            self.__anode, self.__alen = _r[1], _r[3]
            self.__aedge = self.__ext + _r[2] if _r[0] and self.__alen else self.__ext + _r[2] + 1
            self.debuginfo('SEARCH results:')
        if dive(self.__ext):
            self.__ext = min(len(self.text) - 1, self.__ext + 1)
            self.debuginfo('DIVE result:')
            return False, i
        else:
            if self.__alen:  # split the edge
                node = Node()  # create a middle node
                n = len(self.nodes)  # node seq no
                aedge = self.nodes[self.__anode].edges[self.text[self.__aedge]]
                node.edges[self.text[aedge.start + self.__alen]] = Edge(n, aedge.start + self.__alen, aedge.end, aedge.des)  # edges for new node
                aedge.end, aedge.des = aedge.start + self.__alen, n  # modify the current path
                node.edges[self.text[self.__ext]] = Edge(n, self.__ext)  # new leaf path
                self.debuginfo('EDGE SPLIT to {} and add a new node {} with edge {}'.format(aedge.start + self.__alen, n, list(node.edges)))
                self.nodes.append(node)
                self.__reminder -= 1
            else:  # first entry point
                self.nodes[self.__anode].edges[self.text[self.__ext]] = Edge(self.__anode, self.__ext)  # new leaf path
                self.debuginfo('NEW EDGE \'{}\' added for node {} from {}'.format(self.text[self.__ext], self.__anode, self.__ext))
                self.__reminder -= 1 if self.__anode else 0
            return apply_suffix_rules(), i + 1

    def debuginfo(self, info, end=0):
        if self.debug:
            print('\n+', info)
            print('(Active node, edge, length), Reminder, Ext, Prenode:',
                  [(self.__anode, (self.__aedge, self.text[self.__aedge] if self.__aedge < len(self.text) else ''), self.__alen),
                   self.__reminder, self.__ext, self.__prenode])
            if end:
                self.display(0, end)
