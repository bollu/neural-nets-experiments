from recurrent.regex import *
from recurrent.nfa import *

def _nfa_from_regex_ascii(r, nfa):
    assert isinstance(r, RegexASCII)
    start = nfa.mk_node()
    end = nfa.mk_node()
    nfa.connect(start, EdgeType.mk_ascii_edge(r.char), end)
    return (start, end)


def _nfa_from_regex_or(r, nfa):
    assert isinstance(r, RegexOr)
    
    (s1, e1) = _nfa_from_regex(r.r1, nfa)
    (s2, e2) = _nfa_from_regex(r.r2, nfa)

    sor = nfa.mk_node()
    eor = nfa.mk_node()

    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s1)
    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s2)

    nfa.connect(e1, EdgeType.mk_epsilon_edge(), eor)
    nfa.connect(e2, EdgeType.mk_epsilon_edge(), eor)

    return (sor, eor)

def _nfa_from_regex_sequence(r, nfa):
    assert isinstance(r, RegexSequence)

    (s1, e1) = _nfa_from_regex(r.r1, nfa)
    (s2, e2) = _nfa_from_regex(r.r2, nfa)

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
def _nfa_from_regex_star(star, nfa):
    assert isinstance(star, StarRegex)

    (s, e) = _nfa_from_regex(star.r, nfa)

    nodestar = nfa.mk_node()
    nfa.connect(nodestar, EdgeType.mk_none_edge(), s)
    nfa.connect(e, EdgeType.mk_epsilon_edge(), nodestar)

    return (nodestar, nodestar)

def _nfa_from_regex(r, nfa):
    assert isinstance(r, Regex)
    assert isinstance(nfa, NFA)

    if isinstance(r, RegexASCII):
        return _nfa_from_regex_ascii(r, nfa)
    elif isinstance(r, RegexOr):
        return _nfa_from_regex_or(r, nfa)
    elif isinstance(r, RegexSequence):
        return _nfa_from_regex_sequence(r, nfa)
    elif isinstance(r, StarRegex):
        return _nfa_from_regex_star(r, nfa)
    else:
        raise RuntimeError("should not reach here, unreachable branch!")

def nfa_from_regex(r):
    nfa = NFA()
    (start, end) = _nfa_from_regex(r, nfa)
    nfa.start_node = start
    nfa.end_node = end
    return nfa


def regex_from_nfa(n):
    n = nfa_prune(n)
    
