from sympy.logic import SOPform
from sympy import symbols

def generate_table():
    header = " q3* q2* q1* | V |  q3  q2  q1 | h3  h2  h1 "
    print(header)
    print("-" * len(header))

    for i in range(16):
        v = i & 1
        q_star_total = (i >> 1) & 0x7
        
        q3_s = (q_star_total >> 2) & 1
        q2_s = (q_star_total >> 1) & 1
        q1_s = (q_star_total >> 0) & 1

        if v == 1:
            q_next_total = (q_star_total + 1) % 8
        else:
            q_next_total = q_star_total

        q3 = (q_next_total >> 2) & 1
        q2 = (q_next_total >> 1) & 1
        q1 = (q_next_total >> 0) & 1

        h3 = q3_s ^ q3
        h2 = q2_s ^ q2
        h1 = q1_s ^ q1

        print(f"  {q3_s}   {q2_s}   {q1_s}  | {v} |  {q3}   {q2}   {q1}  | {h3}   {h2}   {h1} ")
        
        
def get_h_values_8_states():
    num_bits = 3
    h_data = {f'h{i+1}': [] for i in range(num_bits)}
    
    for i in range(16):
        v = i & 1               
        q_star = (i >> 1) & 0x7 
        
        q_next = (q_star + 1) % 8 if v == 1 else q_star
        
        for bit in range(num_bits):
            qs = (q_star >> bit) & 1
            qn = (q_next >> bit) & 1
            h_data[f'h{bit+1}'].append(qs ^ qn)
            
    return h_data

def format_logic(expr):
    s = str(expr)
    s = s.replace('&', '•')
    s = s.replace('|', '+')
    s = s.replace('~', '!') 
    return s

def print_k_map_4x4(h_name, values):
    gray = [0, 1, 3, 2]
    
    print(f"\nДиаграмма Вейча-Карно для {h_name}:")
    print(" q3*q2* \\ q1*V | 00 | 01 | 11 | 10 |")
    print("-" * 37)
    
    for r in gray:
        row_label = bin(r)[2:].zfill(2)
        row_str = f"           {row_label}  | "
        for c in gray:
            idx = (r << 2) | c
            val = values[idx]
            row_str += f" {val}   "
        print(row_str)

def run_synthesis():
    q3, q2, q1, v = symbols('q3* q2* q1* v')
    variables = [q3, q2, q1, v]
    
    h_results = get_h_values_8_states()
    
    print("-" * 45)
    
    for h_name in ['h3', 'h2', 'h1']:
        vals = h_results[h_name]
        
        print_k_map_4x4(h_name, vals)
        
        min_indices = [i for i, val in enumerate(vals) if val == 1]
        if not min_indices:
            minimized = "0"
        else:
            minimized = SOPform(variables, min_indices)
            
        print(f"\n{h_name} = {format_logic(minimized)}")
        print("=" * 45)

if __name__ == "__main__":
    print("Входы: 4")
    print("Выходы: 3")
    print("Элементы памяти: 3\n")
    generate_table()
    run_synthesis()