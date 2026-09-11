"""
Лабораторная работа №6 — Моделирование таблиц хеширования
Вариант 8: Транспорт
Ключевые слова (ID): виды/термины транспорта
Данные (Pi): определение или описание
"""

from email.policy import default


TABLE_SIZE = 20  # H — количество строк таблицы
BASE_ADDR = 0    # B — начальный адрес

# Алфавит: русский (А=0 ... Я=32), всего 33 символа
ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
BASE = len(ALPHABET)  # 33

# ---------- Исходные данные (не менее 10 ключевых слов) ----------
INITIAL_DATA = [
    ("Автобус",    "Безрельсовое колёсное транспортное средство вместимостью более 8 пассажиров"),
    ("Трамвай",    "Рельсовый городской электрический транспорт, движущийся по улицам"),
    ("Троллейбус", "Безрельсовый городской электрический транспорт на резиновых шинах"),
    ("Метро",      "Городской рельсовый транспорт, проходящий преимущественно под землёй"),
    ("Самолёт",    "Воздушное судно тяжелее воздуха с двигателем и неподвижным крылом"),
    ("Теплоход",   "Судно с двигателем внутреннего сгорания для перевозки по воде"),
    ("Трактор",    "Самоходная машина для буксировки прицепов и привода орудий"),
    ("Мотоцикл",   "Двухколёсное механическое транспортное средство с двигателем"),
    ("Такси",      "Автомобиль с таксометром для перевозки пассажиров за плату"),
    ("Автомобиль", "Безрельсовое транспортное средство с двигателем для 1–8 пассажиров"),
    ("Трамплин",   "Устройство для прыжков; используется в велоспорте и мотоспорте"),
    ("Маршрутка",  "Микроавтобус, курсирующий по фиксированному городскому маршруту"),
]


# ================================================================
#  Вспомогательные функции
# ============================Развернуть====================================

def key_value(word: str) -> int:
    """V = первая_буква * BASE + вторая_буква  (позиционная система счисления)."""
    w = word.upper()
    idx0 = ALPHABET.find(w[0]) if len(w) > 0 else 0
    idx1 = ALPHABET.find(w[1]) if len(w) > 1 else 0
    if idx0 < 0: idx0 = 0
    if idx1 < 0: idx1 = 0
    return idx0 * BASE + idx1


def hash_addr(v: int) -> int:
    """h(V) = V mod H + B"""
    return v % TABLE_SIZE + BASE_ADDR


# ================================================================
#  Структура ячейки хеш-таблицы
# ================================================================

def empty_cell():
    """Возвращает пустую ячейку (строку) хеш-таблицы."""
    return {
        "ID": None,   # ключевое слово
        "C":  0,      # флажок коллизии
        "U":  0,      # флажок «занято»
        "T":  0,      # терминальный флажок (1 = последняя/единственная в цепочке)
        "L":  0,      # флажок связи (0 = Pi содержит данные)
        "D":  0,      # флажок вычеркивания
        "P0": None,   # указатель следующей строки в цепочке
        "Pi": None,   # данные
    }


# Инициализация таблицы
table: list[dict] = [empty_cell() for _ in range(TABLE_SIZE)]


# ================================================================
#  Основные операции
# ================================================================

def _find_free(start: int) -> int | None:
    """Линейный пробинг — поиск свободной ячейки начиная с start."""
    for delta in range(1, TABLE_SIZE):
        idx = (start + delta) % TABLE_SIZE
        if table[idx]["U"] == 0:
            return idx
    return None  # таблица полна


def insert(keyword: str, data: str) -> str:
    """Вставка новой записи в хеш-таблицу."""
    v = key_value(keyword)
    h = hash_addr(v)

    # Проверка дубликата
    existing = search(keyword)
    if existing is not None:
        return f"[ОШИБКА] Ключ «{keyword}» уже существует в строке {existing}."

    target = h
    cell = table[target]

    if cell["U"] == 0:
        cell["ID"] = keyword
        cell["U"]  = 1
        cell["C"]  = 0
        cell["T"]  = 1      
        cell["D"]  = 0
        cell["P0"] = h      
        cell["Pi"] = data
        return f"Запись «{keyword}» -> строка {target} (h={h}, V={v})"
    else:
        reserve = _find_free(h)
        if reserve is None:
            return "[ОШИБКА] Таблица переполнена!"

        reserve_cell = table[reserve]
        reserve_cell["ID"] = keyword
        reserve_cell["U"]  = 1
        reserve_cell["T"]  = 1   # конец новой цепочки
        reserve_cell["D"]  = 0
        reserve_cell["P0"] = h   # ссылается на хеш-адрес основной записи
        reserve_cell["Pi"] = data

        # Дойдём до конца существующей цепочки и добавим ссылку
        cur = target
        table[target]["C"]  = 1
        while table[cur]["T"] == 0 and table[cur]["P0"] is not None:
            cur = table[cur]["P0"]
        # cur — последняя в цепочке
        table[cur]["T"]  = 0
        table[cur]["P0"] = reserve  # ссылка на новую резервную ячейку

        return (f"Коллизия! «{keyword}» -> резервная строка {reserve} "
                f"(h={h}, V={v}, цепочка от строки {target})")


def search(keyword: str) -> int | None:
    """Поиск ключевого слова. Возвращает индекс строки или None."""
    v = key_value(keyword)
    h = hash_addr(v)
    idx = h
    visited = set()

    while idx is not None and idx not in visited:
        visited.add(idx)
        cell = table[idx]
        if cell["U"] == 0:
            # Свободная ячейка — запись не найдена
            return None
        if cell["D"] == 0 and cell["ID"] == keyword:
            return idx
        if cell["T"] == 1:
            # Конец цепочки
            return None
        idx = cell["P0"]

    return None


def delete(keyword: str) -> str:
    """Удаление записи по ключевому слову."""
    idx = search(keyword)
    if idx is None:
        return f"[ОШИБКА] Ключ «{keyword}» не найден."

    cell = table[idx]

    if cell["T"] == 1 and cell["P0"] == idx:
        # Одиночная запись — просто освобождаем
        table[idx] = empty_cell()
        return f"Строка {idx} («{keyword}») удалена (одиночная запись)."

    elif cell["T"] == 1:
        # Последняя в цепочке — найти предыдущую
        h = hash_addr(key_value(keyword))
        prev = h
        visited = set()
        while table[prev]["P0"] != idx and prev not in visited:
            visited.add(prev)
            if table[prev]["T"] == 1:
                break
            prev = table[prev]["P0"]
        table[prev]["T"]  = 1
        table[prev]["C"]  = 0
        table[prev]["P0"] = h   # указывает на базовый адрес
        table[idx] = empty_cell()
        return f"Строка {idx} («{keyword}») удалена (была последней в цепочке)."

    else:
        next_idx = cell["P0"]
        next_cell = table[next_idx]
        table[idx]["ID"] = next_cell["ID"]
        table[idx]["C"]  = next_cell["C"]
        table[idx]["T"]  = next_cell["T"]
        table[idx]["D"]  = next_cell["D"]
        table[idx]["P0"] = next_cell["P0"]
        table[idx]["Pi"] = next_cell["Pi"]
        table[next_idx] = empty_cell()
        return (f"Строка {idx} («{keyword}») удалена; "
                f"на её место перемещена строка {next_idx} («{table[idx]['ID']  }»).")


def fill_factor() -> float:
    """Коэффициент заполнения = занятые строки / всего строк."""
    occupied = sum(1 for c in table if c["U"] == 1)
    return occupied / TABLE_SIZE


# ================================================================
#  Отображение таблицы
# ================================================================

def print_table():
    """Вывод всей хеш-таблицы в консоль."""
    print("\n" + "═" * 90)
    print(f"{'№':>3} | {'ID':<14} | C | U | T | L | D | {'P0':>4} | Данные (Pi)")
    print("─" * 90)
    for i, c in enumerate(table):
        if c["U"] == 0:
            print(f"{i:>3} | {'—':<14} | - | 0 | - | - | - | {'—':>4} | —")
        else:
            print(
                f"{i:>3} | {str(c['ID']):<14} | "
                f"{c['C']} | {c['U']} | {c['T']} | {c['L']} | {c['D']} | "
                f"{str(c['P0']):>4} | {c['Pi']}"
            )
    print("═" * 90)
    print(f"Коэффициент заполнения: {fill_factor():.2%}")
    print()


def print_vhash(keyword: str):
    """Вывод V и h для конкретного ключевого слова."""
    v = key_value(keyword)
    h = hash_addr(v)
    print(f"  «{keyword}»: V={v}, h(V)={h}")


# ================================================================
#  Интерактивное меню
# ================================================================

def menu():
    while True:
        print("\n╔══════════════════════════════╗")
        print("║   ХЕШ-ТАБЛИЦА «ТРАНСПОРТ»    ║")
        print("╠══════════════════════════════╣")
        print("║ 1. Показать таблицу          ║")
        print("║ 2. Вставить запись           ║")
        print("║ 3. Найти запись              ║")
        print("║ 4. Удалить запись            ║")
        print("║ 5. V и h для ключевого слова ║")
        print("║ 6. Выход                     ║")
        print("╚══════════════════════════════╝")
        choice = input("Выбор: ").strip()

        match(choice):
            case "1":
                print_table()

            case "2":
                kw   = input("Ключевое слово: ").strip()
                data = input("Данные: ").strip()
                print(insert(kw, data))

            case "3":
                kw = input("Ключевое слово: ").strip()
                idx = search(kw)
                if idx is None:
                    print(f"Запись «{kw}» не найдена.")
                else:
                    c = table[idx]
                    print(f"Найдено в строке {idx}: данные → {c['Pi']}")

            case "4":
                kw = input("Ключевое слово для удаления: ").strip()
                print(delete(kw))

            case "5":
                kw = input("Ключевое слово: ").strip()
                print_vhash(kw)

            case "6":
                print("До свидания!")
                break
            case _:
                print("Неверный ввод.")



if __name__ == "__main__":
    print("=== Формирование начальной хеш-таблицы ===")
    for keyword, data in INITIAL_DATA:
        result = insert(keyword, data)
        v = key_value(keyword)
        h = hash_addr(v)
        print(f"  {result}")

    print_table()
    menu()