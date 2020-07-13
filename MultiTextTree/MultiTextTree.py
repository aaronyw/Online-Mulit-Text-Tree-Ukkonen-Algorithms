from bisect import bisect
from MultiTextTree.Ukkonen import *


class Multxtree:
    def __init__(self, ukkonen=True, shift=0x10000):
        self.shift = shift
        self.id = 0
        self.type = ukkonen
        self.tree = Ukkonen() if self.type else Radix()
        self.index = [0]

    def read(self, text):
        self.id += 1
        if self.id == (1<<21) - self.shift:
            raise ValueError('Reached the message limit %s'.format(1<<21))
        self.tree.read(text, chr(self.id + self.shift))
        self.index.append(len(self.tree.text))

    def search(self, text, limit=1<<21):

        def rake(_i):
            _b, _s, _l = self.tree.nodes[_i[0]].children()
            _s = [_ + _i[1] for _ in _s]
            return list(zip(_b, _s)), [_ - _i[1] for _ in _l]

        f, n, e, p, _ = self.tree.search(text)  # flag, node, edge, pointer on that edge
        r, shift = {}, 0
        if f:
            if p:  # if searched text are on an edge
                edge = self.tree.nodes[n].edges[text[e]]
                if edge.end:
                    shift = edge.end - edge.start - p
                    n = edge.des
                else:
                    return {bisect(self.index, edge.start + p): [edge.start + p]}
            q = [(n, shift)]
            i = 0
            while i < len(q) and len(r) <= limit:
                _q, _r = rake(q[i])
                q += _q
                for _i in _r:
                    k = bisect(self.index, _i)
                    if k not in r:
                        r[k] = []
                    r[k].append(_i)
                i += 1
        return r

    def extractxt(self, i, highlighter=(0, [])):
        '''
        :param i: tree id
        :param highlighter: (highlighter length, [highlighter positions]
        :return: array of non highlighted text in segments
        '''
        _s = self.index[i - 1]
        r = []
        for _h in sorted(highlighter[1]):
            r.append(self.tree.text[_s:_h - highlighter[0]])
            _s = _h
        return r + [self.tree.text[_s:self.index[i] - 1]]
