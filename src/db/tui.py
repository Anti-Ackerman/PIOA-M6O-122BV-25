from .backend.memory import Database, Record

class CarDatabaseUI:

    def __init__(self):
        self.db = Database()
        self.fields = ["brand", "price", "color"] 

    def run(self):
        print("=" * 50)
        print("   Добро пожаловать в БД АВТОМОБИЛЕЙ (in-memory)")
        print("=" * 50)
        try:
            self.db.create_table("cars")
            print("Автоматически создана таблица 'cars' с полями: brand, price, color")
        except ValueError:
            print("Таблица 'cars' уже существует.")

        while True:
            print("\n" + "=" * 30)
            print("ГЛАВНОЕ МЕНЮ")
            print("1. Управление таблицами")
            print("2. Работа с таблицей")
            print("3. Сортировка записей")  
            print("0. Выход")
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                name = self._get_non_empty("Имя новой таблицы: ")
                try:
                    self.db.create_table(name)
                    print(f"Таблица '{name}' создана.")   
                except ValueError as e:
                    print(e)
            elif choice == "2":
                tables = self.db.get_table_names()
                if not tables:
                    print("Нет таблиц.")
                    continue
                print("Доступные:", ", ".join(tables))
                name = input("Имя таблицы для удаления: ").strip()
                try:
                    self.db.drop_table(name)
                    print(f"Таблица '{name}' удалена.")  
                except ValueError as e:
                    print(e)
            elif choice == "3":
                self._sort_table()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный ввод.")

    def _get_non_empty(self, prompt: str) -> str:
        while True:
            val = input(prompt).strip()
            if val:
                return val
            print("Ошибка: поле не может быть пустым.")

    def _get_int(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите целое число.")

    def _get_filters(self) -> Record:
        print("\nВведите критерии поиска (Enter - пропустить):")
        filters = {}
        for f in self.fields:
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

    def _get_data(self) -> Record:
        print("\nВведите данные автомобиля:")
        data = {}
        for f in self.fields:
            if f == "price":
                data[f] = self._get_int(f"{f}: ")
            else:
                data[f] = self._get_non_empty(f"{f}: ")
        return data

    def _print_records(self, records: list[Record]) -> None:
        if not records:
            print("\nАвтомобили не найдены.")
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

    def _table_management(self) -> None:
        while True:
            print("\n--- Управление таблицами ---")
            print("1. Создать таблицу")
            print("2. Удалить таблицу")
            print("3. Показать все таблицы")
            print("0. Назад в главное меню")
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                name = self._get_non_empty("Имя новой таблицы: ")
                try:
                    self.db.create_table(name)
                except ValueError as e:
                    print(e)
            elif choice == "2":
                tables = self.db.get_table_names()
                if not tables:
                    print("Нет таблиц.")
                    continue
                print("Доступные:", ", ".join(tables))
                name = input("Имя таблицы для удаления: ").strip()
                try:
                    self.db.drop_table(name)
                except ValueError as e:
                    print(e)
            elif choice == "3":
                tables = self.db.get_table_names()
                if tables:
                    print("Таблицы:", ", ".join(tables))
                else:
                    print("Таблицы отсутствуют.")
            elif choice == "0":
                break
            else:
                print("Неверный ввод.")

    def _work_with_table(self, table_name: str) -> None:
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
                    data = self._get_data()
                    rec = self.db.create_record(table_name, data)
                    print(f"Добавлен: ID={rec['id']}, {rec['brand']}, {rec['price']} руб., {rec['color']}")
                except ValueError as e:
                    print(e)
            elif choice == "2":
                filters = self._get_filters()
                res = self.db.read_records(table_name, filters)
                self._print_records(res)
            elif choice == "3":
                print("--- Шаг 1: найти записи для изменения ---")
                filters = self._get_filters()
                old = self.db.read_records(table_name, filters)
                self._print_records(old)
                if old:
                    print("--- Шаг 2: введите новые данные ---")
                    new_data = self._get_data()
                    cnt = self.db.update_records(table_name, filters, new_data)
                    print(f"Обновлено записей: {cnt}")
                else:
                    print("Нет записей по заданному фильтру.")
            elif choice == "4":
                print("--- Найти записи для удаления ---")
                filters = self._get_filters()
                to_del = self.db.read_records(table_name, filters)
                self._print_records(to_del)
                if to_del:
                    confirm = input("Удалить эти записи? (y/N): ").strip().lower()
                    if confirm == "y":
                        cnt = self.db.delete_records(table_name, filters)
                        print(f"Удалено записей: {cnt}")
                    else:
                        print("Удаление отменено.")
                else:
                    print("Нет записей по фильтру.")
            elif choice == "5":
                all_rec = self.db.read_records(table_name)
                self._print_records(all_rec)
            elif choice == "6":
                break
            elif choice == "0":
                return
            else:
                print("Неверный ввод.")

    def _choose_and_work_with_table(self) -> None:
        tables = self.db.get_table_names()
        if not tables:
            print("Нет таблиц. Сначала создайте таблицу через пункт 1.")
            return
        print("Доступные таблицы:", ", ".join(tables))
        name = input("Введите имя таблицы: ").strip()
        if name in tables:
            self._work_with_table(name)
        else:
            print(f"Таблица '{name}' не найдена.")

    def _sort_table(self) -> None:
        tables = self.db.get_table_names()
        if not tables:
            print("Нет таблиц для сортировки.")
            return
        print("Доступные таблицы:", ", ".join(tables))
        table_name = input("Имя таблицы: ").strip()
        if table_name not in tables:
            print("Таблица не найдена.")
            return

        records = self.db.read_records(table_name)
        if not records:
            print("Таблица пуста, нечего сортировать.")
            return

        sample = records[0] 
        available_fields = [key for key in sample.keys() if key != 'id']
        print("Доступные поля для сортировки:", ", ".join(available_fields))

        key = input("Поле для сортировки: ").strip()
        if key not in available_fields:
            print("Недопустимое поле.")
            return

        rev_input = input("По убыванию? (y/N): ").strip().lower()
        reverse = (rev_input == 'y')

        try:
            sorted_records = self.db.sort_records(table_name, key, reverse)
            self._print_records(sorted_records)
        except ValueError as e:
            print(e)