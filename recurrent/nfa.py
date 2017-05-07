import string
import pprint

class EdgeType:
    _NONE_EDGE_VAL = 0
    _EPSILON_EDGE_VAL = 1

    def __init__(self, val):
        self._int_val = val

    def __str__(self):
        if self._int_val == EdgeType._NONE_EDGE_VAL:
            return "None"
        elif self._int_val == EdgeType._EPSILON_EDGE_VAL:
            return "eps"
        else:
            return chr(self._int_val)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self._int_val == other._int_val

    @staticmethod
    def from_int(val):
        assert isinstance(val, int)
        if val == EdgeType._NONE_EDGE_VAL:
            return EdgeType.mk_none_edge()
        elif val == EdgeType._EPSILON_EDGE_VAL:
            return EdgeType.mk_epsilon_edge()
        else:
            return EdgeType.mk_ascii_edge(chr(val))

    @property
    def to_int(self):
        return self._int_val

    @staticmethod
    def mk_none_edge():
        return EdgeType(EdgeType._NONE_EDGE_VAL)

    @staticmethod
    def mk_epsilon_edge():
        return EdgeType(EdgeType._EPSILON_EDGE_VAL)

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


def nfa_to_dot(nfa):
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


def adj_matrix_from_nfa(nfa, num_nodes):
    if nfa.numnodes > num_nodes:
        raise RuntimeError("NFA has %s nodes, > expected (%s)" %
                           (nfa.numnodes, num_nodes))

    adj = [[EdgeType.mk_none_edge().to_int for _ in range(num_nodes)]
            for _ in range(num_nodes)]

    for c in nfa.connections:
        adj[c.src.idx][c.dest.idx] = c.edge.to_int

    return adj


def nfa_from_adjacency_matrix(adj):
    assert len(adj) > 0
    assert len(adj[0]) > 0
    assert len(adj) == len(adj[0])

    for row in adj[1:]:
        assert len(adj[0]) == len(row)

    nfa = NFA()

    nodes = [nfa.mk_node() for _ in range(len(adj))]

    for (si, row) in enumerate(adj):
        for (ei, col) in enumerate(row):
            edgeval = col
            nfa.connect(nodes[si], EdgeType.from_int(edgeval), nodes[ei])

    return nfa

def nfa_prune(nfa):
    used_nodes = set()

    for c in nfa.connections:
        if c.edge == EdgeType.mk_none_edge():
            continue
        used_nodes.add(c.src.idx)
        used_nodes.add(c.dest.idx)

    prunednfa = NFA()
    old_id_to_new_node = dict([(idx, prunednfa.mk_node()) for idx in used_nodes])
    print("NFA:\n%s" % nfa)
    print("remap: %s" % pprint.pformat(old_id_to_new_node))

    for c in nfa.connections:
        if c.edge == EdgeType.mk_none_edge():
            continue

        print("c: %s\n" % (c, ))
        prunednfa.connect(old_id_to_new_node[c.src.idx],
                          c.edge,
                          old_id_to_new_node[c.dest.idx])

    return prunednfa