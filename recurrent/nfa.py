import string
import pprint

class EdgeType:
    _NONE_EDGE_VAL = 0
    _EPSILON_EDGE_VAL = 1

    def __init__(self, val):
        self._val = val

    def __str__(self):
        if self._val == EdgeType._NONE_EDGE_VAL:
            return "None"
        elif self._val == EdgeType._EPSILON_EDGE_VAL:
            return "eps"
        else:
            return chr(self._val)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def mk_none_edge():
        return EdgeType(0)

    @staticmethod
    def mk_epsilon_edge():
        return EdgeType(1)

    @staticmethod
    def mk_ascii_edge(c):
        chars = string.ascii_letters + string.digits + string.punctuation
        assert c in chars, "%s is not a valid char" % (c, )

        weight =  ord(c)
        assert weight >= 2, "%s = %s:%s is incorrect" % (weight, c, ord(c))

        return EdgeType(weight)


class NFANode:
    def __init__(self, idx):
        self._idx = idx

    @property
    def idx(self):
        return self._idx

    def __str__(self):
        return "%s" % self._idx

    def __repr__(self):
        return self.__str__()

class Connection:
    def __init__(self, src, edge, dest):
        assert isinstance(src, NFANode)
        assert isinstance(dest, NFANode)
        assert isinstance(edge, EdgeType)

        self._src = src
        self._dest = dest
        self._edge = edge

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, new):
        assert isinstance(new, NFANode)
        self._src = new

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, new):
        assert isinstance(new, NFANode)
        self._dest = new

    @property
    def edge(self):
        return self._edge

    def __str__(self):
        return "%s -(%s)-> %s" % (self._src, self._edge, self._dest)

    def __repr__(self):
        return self.__str__()

class NFA:
    def __init__(self):
        self._connections = []
        self._numnodes = 0
        self._start_node = None
        self._end_node = None

    @property
    def connections(self):
        return self._connections

    @property
    def numnodes(self):
        return self._numnodes

    @property
    def start_node(self):
        return self._start_node

    @start_node.setter
    def start_node(self, node):
        assert isinstance(node, NFANode)
        self._start_node = node

    @property
    def end_node(self):
        return self._end_node

    @end_node.setter
    def end_node(self, node):
        assert isinstance(node, NFANode)
        self._end_node = node
        
    def __str__(self):
        return "numNodes: %s\n%s" % (self._numnodes, pprint.pformat(self._connections))

    def __repr__(self):
        return self.__str__()

    def connect(self, src, edge, dest):
        self._connections.append(Connection(src, edge, dest))

    def mk_node(self):
        node = NFANode(self._numnodes)
        self._numnodes += 1

        return node


def make_nfa_dot(nfa):
    from graphviz import Digraph
    dot = Digraph(comment='NFA')

    dot.attr(rankdir='LR', size='8,5')

    dot.attr("graph", overlap="false", splines="true")
    dot.attr("node", shape="circle")
    
    dot.attr("graph", fontname="Courier")
    dot.attr("node", fontname="Courier")
    dot.attr("edge", fontname="Courier")
    
    for i in range(nfa.numnodes):
        attrs = {}

        if (i == nfa.start_node.idx):
            attrs["shape"] = "doublecircle"
        if (i == nfa.end_node.idx):
            attrs["style"] = "filled"
            attrs["color"] = "#CCCCCC"
            
        dot.node(str(i), **attrs)


    for connect in nfa.connections:
        dot.edge(str(connect.src.idx), str(connect.dest.idx), xlabel=str(connect.edge))

    return dot


