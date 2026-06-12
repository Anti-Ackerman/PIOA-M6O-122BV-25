from .backend.memory import Database, Record

db = Database()
CARS_FIELDS = ["brand", "price", "color"] 

def _get_non_empty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Ошибка: поле не может быть пустым.")

def _get_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите целое число.")

def _get_filters(fields: list[str]) -> Record:
    print("\nВведите критерии поиска (Enter - пропустить):")
    filters = {}
    for f in fields:
        if f == "price":
            val = input(f"{f} (целое): ").strip()
            if val:
                try:
                    filters[f] = int(val)
                except ValueError:
                    print(f"  (фильтр по {f} пропущен, нужно целое число)")
        else:
            val = input(f"{f}: ").strip()
            if val:
                filters[f] = val
    return filters

def _get_data(fields: list[str]) -> Record:
    print("\nВведите данные автомобиля:")
    data = {}
    for f in fields:
        if f == "price":
            data[f] = _get_int(f"{f}: ")
        else:
            data[f] = _get_non_empty(f"{f}: ")
    return data

def _print_records(records: list[Record]) -> None:
    if not records:
        print("\n Автомобили не найдены.")
        return
    print("\n" + "=" * 50)
    print(f"{'ID':<5} {'Марка':<15} {'Цена':<12} {'Цвет':<10}")
    print("-" * 50)
    for r in records:
        print(f"{r.get('id', '-'):<5} "
              f"{r.get('brand', '-'):<15} "
              f"{r.get('price', '-'):<12} "
              f"{r.get('color', '-'):<10}")
    print("=" * 50)

def _table_management() -> str | None:
    while True:
        print("\n--- Управление таблицами ---")
        print("1. Создать таблицу")
        print("2. Удалить таблицу")
        print("3. Показать все таблицы")
        print("4. Выбрать таблицу для работы")
        print("0. Назад в главное меню")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            name = _get_non_empty("Имя новой таблицы: ")
            try:
                db.create_table(name)
            except ValueError as e:
                print(f"{e}")
        elif choice == "2":
            tables = db.get_table_names()
            if not tables:
                print("Нет таблиц.")
                continue
            print("Доступные:", ", ".join(tables))
            name = input("Имя таблицы для удаления: ").strip()
            try:
                db.drop_table(name)
            except ValueError as e:
                print(f"{e}")
        elif choice == "3":
            tables = db.get_table_names()
            if tables:
                print("Таблицы:", ", ".join(tables))
            else:
                print("Таблицы отсутствуют.")
        elif choice == "4":
            tables = db.get_table_names()
            if not tables:
                print("Нет таблиц. Сначала создайте таблицу.")
                continue
            print("Доступные:", ", ".join(tables))
            name = input("Имя таблицы для работы: ").strip()
            if name in tables:
                return name
            else:
                print(f"Таблица '{name}' не найдена.")
        elif choice == "0":
            return None
        else:
            print("Неверный ввод.")

def _data_management(table_name: str, fields: list[str]) -> None:
    while True:
        print(f"\n--- Работа с таблицей '{table_name}' (автомобили) ---")
        print("1. Добавить автомобиль")
        print("2. Найти автомобили")
        print("3. Обновить автомобили")
        print("4. Удалить автомобили")
        print("5. Показать все автомобили")
        print("6. Выбрать другую таблицу")
        print("0. Назад в главное меню")
        choice = input("Ваш выбор: ").strip()
        if choice == "1":        
            try:
                data = _get_data(fields)
                rec = db.create_record(table_name, data)
                print(f"Добавлен: ID={rec['id']}, {rec['brand']}, {rec['price']} руб., {rec['color']}")
            except ValueError as e:
                print(f"{e}")
        elif choice == "2":     
            f = _get_filters(fields)
            res = db.read_records(table_name, f)
            _print_records(res)
        elif choice == "3":      
            print("--- Шаг 1: найти записи для изменения ---")
            f = _get_filters(fields)
            old = db.read_records(table_name, f)
            _print_records(old)
            if old:
                print("--- Шаг 2: введите новые данные ---")
                new_data = _get_data(fields)
                cnt = db.update_records(table_name, f, new_data)
                print(f"Обновлено записей: {cnt}")
            else:
                print("Нет записей по заданному фильтру.")
        elif choice == "4":     
            print("--- Найти записи для удаления ---")
            f = _get_filters(fields)
            to_del = db.read_records(table_name, f)
            _print_records(to_del)
            if to_del:
                confirm = input("Удалить эти записи? (y/N): ").strip().lower()
                if confirm == "y":
                    cnt = db.delete_records(table_name, f)
                    print(f"Удалено записей: {cnt}")
                else:
                    print("Удаление отменено.")
            else:
                print("Нет записей по фильтру.")
        elif choice == "5":
            all_rec = db.read_records(table_name)
            _print_records(all_rec)
        elif choice == "6":
            break
        elif choice == "0":
            return
        else:
            print("Неверный ввод.")

def run() -> None:
    print("=" * 50)
    print("   Добро пожаловать в БД АВТОМОБИЛЕЙ (in-memory)")
    print("=" * 50)
    try:
        db.create_table("cars")
        print("Автоматически создана таблица 'cars' с полями: brand, price, color")
    except ValueError:
        print("Таблица 'cars' уже существует.")
    while True:
        print("\n" + "=" * 30)
        print("ГЛАВНОЕ МЕНЮ")
        print("1. Управление таблицами")
        print("2. Работа с таблицей")
        print("0. Выход")
        main_choice = input("Выберите действие: ").strip()
        if main_choice == "1":
            selected = _table_management()
            if selected:
                _data_management(selected, CARS_FIELDS.copy())
        elif main_choice == "2":
            tables = db.get_table_names()
            if not tables:
                print("Нет таблиц. Сначала создайте таблицу через пункт 1.")
                continue
            print("Доступные таблицы:", ", ".join(tables))
            name = input("Введите имя таблицы: ").strip()
            if name in tables:
                _data_management(name, CARS_FIELDS.copy())
            else:
                print(f"Таблица '{name}' не найдена.")
        elif main_choice == "0":
            print("До свидания!")
            break
        else:
            print("Неверный ввод.")