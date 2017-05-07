import random
import string

class Regex:
    def generate_text(self, cost):
        raise NotImplementedError

    def make_nfa(self):
        raise NotImplementedError

    def to_int(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

class ASCIIRegex(Regex):
    def __init__(self, c):
        self._c = c

    @property
    def char(self):
        return self._c

    def __str__(self):
        return str(self._c)

    def generate_text(self, cost):
        return str(self._c)

class OrRegex(Regex):
    def __init__(self, r1, r2):
        assert isinstance(r1, Regex)
        assert isinstance(r2, Regex), "%s is not a regex" % (r2, )

        self.r1 = r1
        self.r2 = r2

    def __str__(self):
        return "(%s|%s)" % (self.r1, self.r2)

    def generate_text(self, cost):
        if random.getrandbits(1) == 0:
            return self.r1.generate_text(cost)
        else:
            return self.r2.generate_text(cost)

class SequenceRegex(Regex):
    def __init__(self, r1, r2):
        assert isinstance(r1, Regex)
        assert isinstance(r2, Regex), "%s is not a regex" % (r2, )

        self.r1 = r1
        self.r2 = r2

    def __str__(self):
        return "%s%s" % (self.r1, self.r2)

    def generate_text(self, cost):
        return self.r1.generate_text(cost) + self.r2.generate_text(cost)


class StarRegex(Regex):
    def __init__(self, r):
        assert isinstance(r, Regex)
        self.r = r

    def __str__(self):
        return "<%s>* " % self.r

    def generate_text(self, cost):
        n = random.randint(0, cost)

        "".join([r.generate_text() for _ in range(n)])



def build_random_regex(num_ors, num_stars, num_seq, min_ascii_in_chunk, max_ascii_in_chunk):
    assert min_ascii_in_chunk > 0
    assert max_ascii_in_chunk > 0
    assert max_ascii_in_chunk >= min_ascii_in_chunk

    if num_ors == 0 and num_stars == 0 and num_seq == 0:
        chars = string.ascii_letters + string.digits + string.punctuation
        asciis = [ASCIIRegex(random.choice(chars)) for _ in range(random.randint(min_ascii_in_chunk, max_ascii_in_chunk))]

        assert len(asciis) > 0
        if len(asciis) == 1:
            return asciis[0]
        
        assert len(asciis) >= 2
        seq = SequenceRegex(asciis[0], asciis[1])
        asciis = asciis[2:]

        for x in asciis:
            seq = SequenceRegex(seq, x)

        return seq
    
    choices = []
    if num_ors > 0:
        choices.append(OrRegex(build_random_regex(num_ors - 1, num_stars, num_seq, min_ascii_in_chunk, max_ascii_in_chunk),
                               build_random_regex(num_ors - 1, num_stars, num_seq, min_ascii_in_chunk, max_ascii_in_chunk)))

    if num_stars > 0:
        choices.append(StarRegex(build_random_regex(num_ors, num_stars - 1, num_seq, min_ascii_in_chunk, max_ascii_in_chunk)))

    if num_seq > 0:
        choices.append(SequenceRegex(build_random_regex(num_ors, num_stars, num_seq - 1, min_ascii_in_chunk, max_ascii_in_chunk),
                                     build_random_regex(num_ors, num_stars, num_seq - 1, min_ascii_in_chunk, max_ascii_in_chunk)))

    return prune_regex(random.choice(choices))


def prune_regex(regex):
    if isinstance(regex, ASCIIRegex):
        return regex
    elif isinstance(regex, StarRegex):
        if isinstance(regex.r, StarRegex):
            return prune_regex(regex.r)
        else:
            return StarRegex(prune_regex(regex.r))
    elif isinstance(regex, SequenceRegex) or isinstance(regex, OrRegex):
        return SequenceRegex(prune_regex(regex.r1), prune_regex(regex.r2))
