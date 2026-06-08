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
        print(f"✓ Таблица '{table_name}' создана.")

    def drop_table(self, table_name: str) -> None:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
        del self._tables[table_name]
        del self._next_ids[table_name]
        print(f"✓ Таблица '{table_name}' удалена.")

    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())

    def create_record(self, table_name: str, data: Record) -> Record:
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует.")
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