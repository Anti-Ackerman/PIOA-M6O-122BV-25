from typing import Any

Record = dict[str, Any]
Table = dict[int, Record]   

class Database:
    def __init__(self) -> None:
        self._tables: dict[str, Table] = {}
        self._next_ids: dict[str, int] = {}

    def create_table(self, table_name: str) -> None:
        if table_name in self._tables:
            raise ValueError(f"Таблица '{table_name}' уже существует.")
        self._tables[table_name] = {}
        self._next_ids[table_name] = 1

    def drop_table(self, table_name: str) -> None:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        del self._tables[table_name]
        del self._next_ids[table_name]

    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())

    def _validate_cars_record(self, data: Record, for_update: bool = False) -> None:
        if for_update:
            if "brand" in data:
                if not isinstance(data["brand"], str) or not data["brand"].strip():
                    raise ValueError("Поле 'brand' не может быть пустым")
            if "price" in data:
                if not isinstance(data["price"], (int, float)):
                    raise ValueError("Поле 'price' должно быть числом")
            if "color" in data:
                if not isinstance(data["color"], str) or not data["color"].strip():
                    raise ValueError("Поле 'color' не может быть пустым")
        else:
            required = {"brand", "price", "color"}
            if not required.issubset(data.keys()):
                missing = required - data.keys()
                raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing)}")
            if not isinstance(data.get("brand"), str) or not data["brand"].strip():
                raise ValueError("Поле 'brand' не может быть пустым")
            if not isinstance(data.get("price"), (int, float)):
                raise ValueError("Поле 'price' должно быть числом")
            if not isinstance(data.get("color"), str) or not data["color"].strip():
                raise ValueError("Поле 'color' не может быть пустым")

    def create_record(self, table_name: str, data: Record) -> Record:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        if table_name == "cars":
            self._validate_cars_record(data, for_update=False)
        
        table = self._tables[table_name]
        new_id = self._next_ids[table_name]
        record = {"id": new_id, **data}
        table[new_id] = record
        self._next_ids[table_name] += 1
        return record

    def read_records(self, table_name: str, filters: Record | None = None) -> list[Record]:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        table = self._tables[table_name]
        records = list(table.values())
        if not filters:
            return records
        filtered = []
        for rec in records:
            match = True
            for key, val in filters.items():
                if val is None or val == "":
                    continue
                rec_val = rec.get(key)
                if isinstance(rec_val, str) and isinstance(val, str):
                    if rec_val.lower() != val.lower():
                        match = False
                        break
                elif rec_val != val:
                    match = False
                    break
            if match:
                filtered.append(rec)
        return filtered

    def update_records(self, table_name: str, filters: Record | None, new_data: Record) -> int:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        if table_name == "cars":
            self._validate_cars_record(new_data, for_update=True)
        
        records = self.read_records(table_name, filters)
        count = 0
        for rec in records:
            for key, val in new_data.items():
                if key != "id":
                    rec[key] = val
            count += 1
        return count

    def delete_records(self, table_name: str, filters: Record | None) -> int:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        table = self._tables[table_name]
        records = self.read_records(table_name, filters)
        count = 0
        for rec in records:
            rid = rec["id"]
            if rid in table:
                del table[rid]
                count += 1
        return count

    def sort_records(self, table_name: str, key: str, reverse: bool = False) -> list[Record]:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        records = list(self._tables[table_name].values())
        if not records:
            return []
        default_value = None
        for rec in records:
            if key in rec:
                val = rec[key]
                if isinstance(val, (int, float)):
                    default_value = 0
                else:
                    default_value = ""
                break
        if default_value is None:
            default_value = ""

        def sort_key(record: Record):
            val = record.get(key)
            if val is None:
                return default_value
            return val
        try:
            return sorted(records, key=sort_key, reverse=reverse)
        except TypeError as e:
            raise TypeError(
                f"Невозможно отсортировать по полю '{key}': "
                f"встречаются значения разных типов. "
                f"Убедитесь, что все записи имеют одинаковый тип данных для этого поля. "
                f"Подробнее: {e}"
            )