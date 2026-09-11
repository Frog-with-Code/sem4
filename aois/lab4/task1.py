import itertools

VARS = ['x1', 'x2', 'x3']
N = len(VARS)


def get_sum(x1: int, x2: int, x3: int) -> int:
    s = x1 + x2 + x3
    return s % 2

def get_carry(x1: int, x2: int, x3: int) -> int:
    c = x1 + x2 + x3
    return c // 2


def build_truth_table():
    return [{'j': j, 'vals': combo, 's': get_sum(*combo), 'c': get_carry(*combo)}
            for j, combo in enumerate(itertools.product([0, 1], repeat=N))]


def term_to_str(term, dnf):
    parts = [VARS[i] if t == 1 else f"!{VARS[i]}" for i, t in enumerate(term) if t != -1]
    if not parts:
        return "1" if dnf else "0"
    return (" * " if dnf else " + ").join(parts)


def form_str(terms, dnf):
    joiner = " + " if dnf else " * "
    parts = [term_to_str(t, dnf) if dnf else f"({term_to_str(t, dnf)})" for t in terms]
    return joiner.join(parts) if parts else ("0" if dnf else "1")


def build_form(table, dnf, key):
    target = 1 if dnf else 0
    return [tuple(v if dnf else 1-v for v in r['vals']) for r in table if r[key] == target]


def try_glue(a, b):
    diff = [i for i in range(N) if a[i] != b[i]]
    if len(diff) != 1: return None
    r = list(a); r[diff[0]] = -1
    return tuple(r)


def quine_reduce(terms):
    cur = list(set(terms))
    while True:
        used, nxt = set(), []
        for i in range(len(cur)):
            for j in range(i+1, len(cur)):
                g = try_glue(cur[i], cur[j])
                if g is not None:
                    used |= {i, j}
                    if g not in nxt: nxt.append(g)
        for i, t in enumerate(cur):
            if i not in used and t not in nxt: nxt.append(t)
        if nxt == cur: break
        cur = nxt
    return cur


def covers(impl, const):
    return all(impl[i] == -1 or impl[i] == const[i] for i in range(N))


def remove_redundant(implicants, constituents):
    res = list(implicants)
    changed = True
    while changed:
        changed = False
        for cand in res[:]:
            others = [t for t in res if t != cand]
            if all(any(covers(o, c) for o in others) for c in constituents if covers(cand, c)):
                res.remove(cand); changed = True; break
    return res


def calc_method(terms, consts, dnf, label):
    reduced = quine_reduce(terms)
    for cand in reduced:
        others = [t for t in reduced if t != cand]
        redundant = all(any(covers(o, c) for o in others) for c in consts if covers(cand, c))
    dead = remove_redundant(reduced, consts)
    return dead



def main():
    table = build_truth_table()
    print("Таблица истинности")
    print(f"{'j':<3} {'x1':<4} {'x2':<4} {'x3':<4} | {'s':<4} {'c':<4} \n{'-'*27}")
    for r in table:
        print(f"{r['j']:<3} {r['vals'][0]:<4} {r['vals'][1]:<4} {r['vals'][2]:<4} | {r['s']:<4} {r['c']}")

    sdnf_s = build_form(table=table, dnf=True, key='s')
    sdnf_c = build_form(table=table, dnf=True, key='c')
    
    print("\ns = " + form_str(sdnf_s, dnf=True))
    print("c = " + form_str(sdnf_c, dnf=True))
    
    print("\nМинимизация")
    s_min = calc_method(sdnf_s, sdnf_s, True, "СДНФ")
    c_min = calc_method(sdnf_c, sdnf_c, True, "СДНФ")

    print("s = " + form_str(s_min, dnf=True))
    print("c = " + form_str(c_min, dnf=True))

if __name__ == "__main__":
    main()