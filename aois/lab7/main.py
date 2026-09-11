import random

def associative_compare(word_S, word_A, n_bits):
    """
    Моделирование логики сравнения ассоциативного процессора (стр. 3-4).
    Возвращает: 1 (S > A), -1 (S < A), 0 (S = A).
    """
    g_prev = 0
    l_prev = 0
    
    # Сравнение идет от старшего разряда (MSB) к младшему (LSB)
    # В списках разряды хранятся [LSB, ..., MSB], поэтому идем в обратном порядке
    for i in range(n_bits - 1, -1, -1):
        a_i = word_A[i]
        S_ji = word_S[i]
        
        # Логические операции согласно формуле (1) из методички
        # Используем битовые операции для имитации работы вентилей И, ИЛИ, НЕ
        g_curr = g_prev | ((1 - a_i) & S_ji & (1 - l_prev))
        l_curr = l_prev | (a_i & (1 - S_ji) & (1 - g_prev))
        
        g_prev = g_curr
        l_prev = l_curr
        
    if g_prev == 1: return 1   # Sj > A
    if l_prev == 1: return -1  # Sj < A
    return 0                   # Sj = A

def int_to_bin_list(val, n_bits):
    """Преобразование числа в список битов (от младшего к старшему)."""
    return [(val >> i) & 1 for i in range(n_bits)]

def bin_list_to_int(bits):
    """Преобразование списка битов обратно в целое число."""
    return sum(bit * (2**i) for i, bit in enumerate(bits))

def perform_sorting(data, n_bits, ascending=True):
    """Упорядоченная выборка (сортировка) на базе ассоциативного сравнения."""
    arr = list(data)
    n = len(arr)
    # Используем алгоритм пузырька, где условие замены основано на ассоциативной логике
    for i in range(n):
        for j in range(0, n - i - 1):
            # Сравниваем S_j (слово в памяти) и S_j+1 (как аргумент A)
            cmp = associative_compare(arr[j], arr[j+1], n_bits)
            
            if (ascending and cmp == 1) or (not ascending and cmp == -1):
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# --- Основной цикл программы ---
M = 8  # Количество слов
N = 8  # Разрядность (8 бит)

# 1. Генерация случайного массива (имитация АЗУ)
memory_array = [int_to_bin_list(random.randint(0, 2**N - 1), N) for _ in range(M)]

print("--- Исходный ассоциативный массив ---")
for row in memory_array:
    print(f"Биты: {row[::-1]} | Десятичное: {bin_list_to_int(row)}")

# 2. Сортировка по возрастанию
sorted_asc = perform_sorting(memory_array, N, ascending=True)
print("\n--- Результат сортировки ПО ВОЗРАСТАНИЮ ---")
for row in sorted_asc:
    print(f"Биты: {row[::-1]} | Десятичное: {bin_list_to_int(row)}")

# 3. Сортировка по убыванию
sorted_desc = perform_sorting(memory_array, N, ascending=False)
print("\n--- Результат сортировки ПО УБЫВАНИЮ ---")
for row in sorted_desc:
    print(f"Биты: {row[::-1]} | Десятичное: {bin_list_to_int(row)}")