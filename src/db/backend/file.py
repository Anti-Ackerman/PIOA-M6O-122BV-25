import json
import os
from pathlib import Path
from typing import Any
from .errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError

Record = dict[str, Any]  

class FileDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.json"

    def _load(self, table_name: str) -> dict:
        path = self._get_path(table_name)
        if not path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError(f"Ошибка JSON: {e}")

    def _save(self, table_name: str, data: dict) -> None:
        path = self._get_path(table_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_table(self, table_name: str) -> None:
        if self._get_path(table_name).exists():
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        self._save(table_name, {"next_id": 1, "records": []})

    def drop_table(self, table_name: str) -> None:
        path = self._get_path(table_name)
        if not path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        os.remove(path)

    def get_table_names(self) -> list[str]:
        return [f.stem for f in self.data_dir.glob("*.json")]

    def create_record(self, table_name: str, data: Record) -> Record:
        table_data = self._load(table_name)
        new_id = table_data["next_id"]
        record = {"id": new_id, **data}
        table_data["records"].append(record)
        table_data["next_id"] = new_id + 1
        self._save(table_name, table_data)
        return record

    def read_records(self, table_name: str, filters: Record | None = None) -> list[Record]:
        table_data = self._load(table_name)
        records = table_data["records"].copy()
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
        to_update = self.read_records(table_name, filters)
        if not to_update:
            return 0
        table_data = self._load(table_name)
        ids = {rec["id"] for rec in to_update}
        updated = 0
        for rec in table_data["records"]:
            if rec["id"] in ids:
                for k, v in new_data.items():
                    if k != "id":
                        rec[k] = v
                updated += 1
        self._save(table_name, table_data)
        return updated

    def delete_records(self, table_name: str, filters: Record | None) -> int:
        to_delete = self.read_records(table_name, filters)
        if not to_delete:
            return 0
        ids = {rec["id"] for rec in to_delete}
        table_data = self._load(table_name)
        original_len = len(table_data["records"])
        table_data["records"] = [rec for rec in table_data["records"] if rec["id"] not in ids]
        deleted = original_len - len(table_data["records"])
        self._save(table_name, table_data)
        return deleted

    def sort_records(self, table_name: str, key: str, reverse: bool = False) -> list[Record]:
        records = self.read_records(table_name)
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

        def sort_key(record: Record) -> Any:
            val = record.get(key)
            if val is None:
                return default_value
            return val
        try:
            return sorted(records, key=sort_key, reverse=reverse)
        except TypeError as e:
            raise TypeError(f"Сортировка по '{key}' невозможна: разные типы данных. {e}")