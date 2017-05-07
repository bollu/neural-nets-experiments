from regex import *
from nfa import *

def _ascii_regex_to_nfa(r, nfa):
    assert isinstance(r, ASCIIRegex)
    start = nfa.mk_node()
    end = nfa.mk_node()
    nfa.connect(start, EdgeType.mk_ascii_edge(r.char), end)
    return (start, end)


def _or_regex_to_nfa(r, nfa):
    assert isinstance(r, OrRegex)
    
    (s1, e1) = _regex_to_nfa(r.r1, nfa)
    (s2, e2) = _regex_to_nfa(r.r2, nfa)

    sor = nfa.mk_node()
    eor = nfa.mk_node()

    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s1)
    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s2)

    nfa.connect(e1, EdgeType.mk_epsilon_edge(), eor)
    nfa.connect(e2, EdgeType.mk_epsilon_edge(), eor)

    return (sor, eor)

def replace_old_nfa_node(nfa, old, new):
    assert isinstance(nfa, NFA)
    assert isinstance(old, NFANode)
    assert isinstance(new, NFANode)

    if old == nfa.start_node:
        nfa.start_node = new

    if old == nfa.end_node:
        nfa.end_node = new

    for c in nfa.connections:
        if c.src == old:
            c.src = new

        if c.dest == old:
            c.dest = new

def _sequence_regex_to_nfa(r, nfa):
    assert isinstance(r, SequenceRegex)

    (s1, e1) = _regex_to_nfa(r.r1, nfa)
    (s2, e2) = _regex_to_nfa(r.r2, nfa)

    nfa.connect(e1, EdgeType.mk_epsilon_edge(), s2)
    # replace_old_nfa_node(nfa, e1, s2)

    return (s1, e2)

#     s -<whatever>-> end
#     ^               |
#     |               eps
#     eps             |
#     |               |
# in->nodestar <------*
#     |
#     |
#     v
#    out
def _star_regex_to_nfa(star, nfa):
    assert isinstance(star, StarRegex)

    (s, e) = _regex_to_nfa(star.r, nfa)

    nodestar = nfa.mk_node()
    nfa.connect(nodestar, EdgeType.mk_none_edge(), s)
    nfa.connect(e, EdgeType.mk_epsilon_edge(), nodestar)

    return (nodestar, nodestar)

def _regex_to_nfa(r, nfa):
    assert isinstance(r, Regex)
    assert isinstance(nfa, NFA)

    if isinstance(r, ASCIIRegex):
        return _ascii_regex_to_nfa(r, nfa)
    elif isinstance(r, OrRegex):
        return _or_regex_to_nfa(r, nfa)
    elif isinstance(r, SequenceRegex):
        return _sequence_regex_to_nfa(r, nfa)
    elif isinstance(r, StarRegex):
        return _star_regex_to_nfa(r, nfa)
    else:
        raise RuntimeError("should not reach here, unreachable branch!")

def regex_to_nfa(r):
    nfa = NFA()
    (start, end) = _regex_to_nfa(r, nfa)
    nfa.start_node = start
    nfa.end_node = end
    return nfa

def nfa_to_regex(nfa):
    pass
