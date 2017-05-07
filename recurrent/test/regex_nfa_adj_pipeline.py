from recurrent import *

r = regex.regex_mk_random(0, 2, 3, 2, 2)
n = regex_nfa_convert.nfa_from_regex(r)

adj = nfa.adj_matrix_from_nfa(n, 40)

n_new = nfa.nfa_from_adjacency_matrix(adj)
n_new = nfa.nfa_prune(n_new)

print("old:\n%s" % n)
print("new:\n%s" % n_new)