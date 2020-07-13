class Node:
    def __init__(self):
        self.edges = {}
        self.suffixlink = 0  # used in Ukkonen Tree only

    def children(self):
        branches, branchlength, leaves = [], [], []
        for edge in self.edges:
            e = self.edges[edge]
            if e.end:
                branches.append(e.des)
                branchlength.append(e.end - e.start)
            else:
                leaves.append(e.start)
        return branches, branchlength, leaves


class Edge:
    def __init__(self, source, start, end=None, des=None):
        self.src = source
        self.start = start
        self.end = end
        self.des = des


class Radix:
    def __init__(self, end='$'):
        self.text = ''
        self.nodes = [Node()]
        self.__etx = end  # end of text

    def read(self, text, end=None):
        i = len(self.text)
        self.text += text + (end if end else self.__etx)
        self.push(i)

    def push(self, i):
        _, n, _e, p, _i = self.search(self.text[i:len(self.text)])
        if p:
            aedge = self.nodes[n].edges[self.text[_e]]
            node = Node()
            _n = len(self.nodes)
            node.edges[self.text[p + aedge.start]] = Edge(_n, p + aedge.start, aedge.end, aedge.des)  # modify the current edge
            node.edges[self.text[_i]] = Edge(_n, len(self.text) + _i)  # new leaf edge
            aedge.end = p + aedge.start
            aedge.des = _n
            self.nodes.append(node)  # new node
        else:
            self.nodes[n].edges[self.text[_e]] = Edge(n, len(self.text) + _i)  # new leaf edge

    def search(self, text, idx=0):
        '''
        private search function used by other functions
        :param text: input text to search in the tree
        :param idx: note to start search
        :return: if searched (T/F), node, -edge char, pointer on edge, -pointer on text
        '''
        if not text:
            return True, idx, -1, 0, 0
        edge = -len(text)
        if text[edge] not in self.nodes[idx].edges:
            return False, idx, edge, 0, -len(text)
        e = self.nodes[idx].edges[text[edge]]
        i = 1
        _end = e.end if e.end else len(self.text)
        while e.start + i < _end:
            if i == len(text):
                return True, idx, edge, i, 0
            elif self.text[e.start + i] != text[i]:
                return False, idx, edge, i, i - len(text)
            i += 1
        return self.search(text[i:], e.des)

    def display(self, i=0, end=None, pre=''):
        print(pre + '|' if pre else '')
        print(pre + 'NODE', i, '\t------> node {}'.format(self.nodes[i].suffixlink) if self.nodes[i].suffixlink else '')
        for edge in self.nodes[i].edges:
            e = self.nodes[i].edges[edge]
            _str = '\t==> node ' + str(e.des) if e.des else ''
            _end = min(e.end, end) if end and e.end else end if end else e.end
            print(pre + '|___', e.src,
                  'edge ' + edge + ': {}->{}\t[{}]'.format(e.start, e.end, self.text[e.start:_end]), _str)
            if e.end:
                self.display(e.des, end, pre + '|    ')
                print(pre + '|    ')
        print(pre + '|___ end of node', i)

    def leaves(self):

        def dfs(i=0):
            res = []
            edges = self.nodes[i].edges
            for e in edges:
                r = dfs(edges[e].des) if edges[e].des else ['']
                for s in r:
                    res.append(self.text[edges[e].start:edges[e].end] + s)
            return res

        if self.text:
            return sorted(dfs(), key=len)
