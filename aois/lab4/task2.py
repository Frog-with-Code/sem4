def build_truth_table(n):
    """Строит таблицу истинности для преобразователя 8421 -> (8421 + n) mod 16"""
    table = []
    for i in range(16):
        x4 = (i >> 3) & 1
        x3 = (i >> 2) & 1
        x2 = (i >> 1) & 1
        x1 = (i >> 0) & 1
        
        if i <= 9:  # Определённые наборы (0-9)
            out = (i + n) % 16
            y4 = (out >> 3) & 1
            y3 = (out >> 2) & 1
            y2 = (out >> 1) & 1
            y1 = (out >> 0) & 1
            defined = True
        else:  # Неопределённые наборы (10-15)
            y4 = y3 = y2 = y1 = 0
            defined = False
            
        table.append({
            'idx': i,
            'x': (x4, x3, x2, x1),
            'y': (y4, y3, y2, y1),
            'defined': defined
        })
    return table


def print_truth_table(table, n):
    print(f"\nТАБЛИЦА ИСТИННОСТИ (8421 -> 8421+{n})")
    print("=" * 35)
    print(" i  | x4 x3 x2 x1 | y4 y3 y2 y1")
    print("-" * 32)
    for row in table:
        i = row['idx']
        x = row['x']
        y = row['y']
        y4 = y[0] if row['defined'] else "-"
        y3 = y[1] if row['defined'] else "-"
        y2 = y[2] if row['defined'] else "-"
        y1 = y[3] if row['defined'] else "-"
        print(f" {i:2d} |  {x[0]}  {x[1]}  {x[2]}  {x[3]} |  {y4}  {y3}  {y2}  {y1}")


def print_karnaugh(table, func_idx, name):
    gray = [(0,0), (0,1), (1,1), (1,0)]
    print(f"\nКарта Карно для {name}:")
    print(" x4x3\\x2x1 | 00 01 11 10")
    print("-------------------------")
    for r in gray:
        cells = []
        print(" "*7, end="")
        for c in gray:
            idx = (r[0]<<3) | (r[1]<<2) | (c[0]<<1) | c[1]
            val = table[idx]['y'][func_idx]
            cells.append("-" if not table[idx]['defined'] else str(val))
        print(f" {r[0]}{r[1]} |  {'  '.join(cells)}")


# ================= МИНИМИЗАЦИЯ =================

def _bits(n):
    return tuple((n >> (3-i)) & 1 for i in range(4))

def _count_ones(t):
    return sum(1 for v in t if v == 1)

def quine_mccluskey(minterms, dont_cares):
    """Возвращает список простых импликант в виде кортежей (v4, v3, v2, v1), где v in {0, 1, -1}"""
    if not minterms:
        return []

    all_terms = [_bits(m) for m in minterms] + [_bits(d) for d in dont_cares]
    
    # Группировка по числу единиц
    groups = {}
    for t in all_terms:
        groups.setdefault(_count_ones(t), []).append(t)

    prime_implicants = []
    while True:
        new_groups = {}
        merged_flags = set()
        keys = sorted(groups.keys())
        
        for i in range(len(keys) - 1):
            for t1 in groups[keys[i]]:
                for t2 in groups[keys[i+1]]:
                    diff = [j for j in range(4) if t1[j] != t2[j]]
                    if len(diff) == 1:
                        pos = diff[0]
                        merged = list(t1)
                        merged[pos] = -1
                        merged = tuple(merged)
                        new_groups.setdefault(_count_ones(merged), []).append(merged)
                        merged_flags.add(t1)
                        merged_flags.add(t2)

        # Те, что не слились -> простые импликанты
        for k in groups:
            for t in groups[k]:
                if t not in merged_flags:
                    prime_implicants.append(t)

        if not new_groups:
            break
        
        # Убираем дубликаты в новой группе
        for k in new_groups:
            new_groups[k] = list(set(new_groups[k]))
        groups = new_groups

    # Отфильтровываем импликанты, покрывающие только don't care
    def covers(pi, m_bits):
        return all(v == -1 or v == m_bits[i] for i, v in enumerate(pi))

    req_bits = [_bits(m) for m in minterms]
    valid_pis = [pi for pi in prime_implicants if any(covers(pi, m) for m in req_bits)]

    # Покрытие минтермов (существенные + жадный выбор)
    selected = []
    covered = set()  # индексы в req_bits
    remaining = list(valid_pis)

    # Поиск существенно необходимых
    changed = True
    while changed:
        changed = False
        for idx, m in enumerate(req_bits):
            if idx in covered: continue
            covering = [pi for pi in remaining if covers(pi, m)]
            if len(covering) == 1:
                pi = covering[0]
                if pi not in selected:
                    selected.append(pi)
                    changed = True
                for r_idx, r_m in enumerate(req_bits):
                    if r_idx not in covered and covers(pi, r_m):
                        covered.add(r_idx)

    # Жадное покрытие остатка
    while len(covered) < len(req_bits):
        best_pi = None
        best_count = 0
        for pi in remaining:
            cnt = sum(1 for idx, m in enumerate(req_bits) if idx not in covered and covers(pi, m))
            if cnt > best_count:
                best_count = cnt
                best_pi = pi
        
        if best_pi is None or best_count == 0:
            break
        selected.append(best_pi)
        remaining.remove(best_pi)
        for idx, m in enumerate(req_bits):
            if idx not in covered and covers(best_pi, m):
                covered.add(idx)

    return selected


def pi_to_dnf_str(pi, vars_names):
    terms = []
    for i, v in enumerate(pi):
        if v == 1: terms.append(vars_names[i])
        elif v == 0: terms.append(f"!{vars_names[i]}")
    return "(" + " * ".join(terms) + ")" if terms else "1"

def pi_to_cnf_str(pi, vars_names):
    # Для КНФ инвертируем значения: 1->!x, 0->x
    terms = []
    for i, v in enumerate(pi):
        if v == 1: terms.append(f"!{vars_names[i]}")
        elif v == 0: terms.append(vars_names[i])
    return "(" + " + ".join(terms) + ")" if terms else "0"


def eval_dnf(pis, x):
    for pi in pis:
        match = True
        for i, v in enumerate(pi):
            if v != -1 and v != x[i]:
                match = False
                break
        if match: return 1
    return 0

def eval_cnf(pis, x):
    # КНФ = конъюнкция дизъюнкций. Ложна, если хотя бы одна скобка ложна.
    # Скобка ложна, когда ВСЕ её литералы ложны.
    # Литерал ложен, когда x[i] == v (так как в импликанте нулей v=1 -> !x, v=0 -> x)
    for pi in pis:
        clause_false = True
        for i, v in enumerate(pi):
            if v != -1:
                if x[i] != v:  # хотя бы один литерал истинен
                    clause_false = False
                    break
        if clause_false:
            return 0
    return 1


def main():
    n = 5
    vars_names = ["x4", "x3", "x2", "x1"]
    func_names = ["y4", "y3", "y2", "y1"]
    
    table = build_truth_table(n)
    print_truth_table(table, n)
    
    for i, name in enumerate(func_names):
        print_karnaugh(table, i, name)

    print("\n" + "="*60)
    print("МИНИМИЗАЦИЯ")
    print("="*60)

    results = {}
    for idx, name in enumerate(func_names):
        minterms = [r['idx'] for r in table if r['defined'] and r['y'][idx] == 1]
        maxterms = [r['idx'] for r in table if r['defined'] and r['y'][idx] == 0]
        dont_cares = [r['idx'] for r in table if not r['defined']]

        print(f"\n{name}:")
        print(f"  Единицы: {minterms}")
        print(f"  Нули:    {maxterms}")
        print(f"  Don't care: {dont_cares}")

        # ТДНФ
        pis_dnf = quine_mccluskey(minterms, dont_cares)
        dnf_str = " v ".join(pi_to_dnf_str(p, vars_names) for p in pis_dnf) if pis_dnf else "0"

        # ТКНФ (минимизируем нули, инвертируем литералы)
        pis_cnf = quine_mccluskey(maxterms, dont_cares)
        cnf_str = " * ".join(pi_to_cnf_str(p, vars_names) for p in pis_cnf) if pis_cnf else "1"

        # Выбираем компактную форму
        len_dnf = len(pis_dnf) if pis_dnf else 999
        len_cnf = len(pis_cnf) if pis_cnf else 999

        if len_cnf <= len_dnf:
            print(f"  ТДНФ: {dnf_str}")
            print(f"  ТКНФ: {cnf_str}  <-- выбрана")
            results[name] = ('cnf', pis_cnf, cnf_str)
        else:
            print(f"  ТДНФ: {dnf_str}  <-- выбрана")
            print(f"  ТКНФ: {cnf_str}")
            results[name] = ('dnf', pis_dnf, dnf_str)

    # ВЕРИФИКАЦИЯ
    print("\n" + "="*60)
    print("ВЕРИФИКАЦИЯ")
    print("="*60)
    print(" i | x4x3x2x1 | ожид |  расч  | ст")
    print("-"*45)
    
    errors = 0
    for row in table:
        if not row['defined']: continue
        x = row['x']
        exp = row['y']
        calc = []
        for name in func_names:
            ftype, pis, _ = results[name]
            val = eval_dnf(pis, x) if ftype == 'dnf' else eval_cnf(pis, x)
            calc.append(val)
        
        ok = calc == list(exp)
        if not ok: errors += 1
        print(f" {row['idx']:2d} | {''.join(map(str,x))}    | {''.join(map(str,exp))}  | {''.join(map(str,calc))}  | {'OK' if ok else 'ERR'}")

    print()
    print("Успешно!" if errors == 0 else f"Ошибок: {errors}")
    
    print("\n" + "="*60)
    print("ИТОГОВЫЕ ФОРМУЛЫ")
    print("="*60)
    for name in func_names:
        print(f"{name} = {results[name][2]}")


if __name__ == "__main__":
    main()