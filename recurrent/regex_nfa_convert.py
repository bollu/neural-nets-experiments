from .regex import *
from .nfa import *

def _regex_ascii_to_nfa(r, nfa):
    assert isinstance(r, RegexASCII)
    start = nfa.mk_node()
    end = nfa.mk_node()
    nfa.connect(start, EdgeType.mk_ascii_edge(r.char), end)
    return (start, end)


def _regex_or_to_nfa(r, nfa):
    assert isinstance(r, RegexOr)
    
    (s1, e1) = _regex_to_nfa(r.r1, nfa)
    (s2, e2) = _regex_to_nfa(r.r2, nfa)

    sor = nfa.mk_node()
    eor = nfa.mk_node()

    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s1)
    nfa.connect(sor, EdgeType.mk_epsilon_edge(), s2)

    nfa.connect(e1, EdgeType.mk_epsilon_edge(), eor)
    nfa.connect(e2, EdgeType.mk_epsilon_edge(), eor)

    return (sor, eor)

def _regex_sequence_to_nfa(r, nfa):
    assert isinstance(r, RegexSequence)

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

    if isinstance(r, RegexASCII):
        return _regex_ascii_to_nfa(r, nfa)
    elif isinstance(r, RegexOr):
        return _regex_or_to_nfa(r, nfa)
    elif isinstance(r, RegexSequence):
        return _regex_sequence_to_nfa(r, nfa)
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

