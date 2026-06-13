import csv
import json
import os
from pathlib import Path
from typing import Any, Optional

Record = dict[str, Any]

class CsvFileDatabase:
    def __init__(self, data_dir: str = "csv_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_csv_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.csv"

    def _get_schema_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.schema.json"

    def _load_schema(self, table_name: str) -> dict:
        path = self._get_schema_path(table_name)
        if not path.exists():
            raise FileNotFoundError(f"Таблица '{table_name}' не существует.")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_schema(self, table_name: str, next_id: int, columns: list[str]) -> None:
        schema = {"next_id": next_id, "columns": columns}
        path = self._get_schema_path(table_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

    def _load_records(self, table_name: str) -> list[Record]:
        path = self._get_csv_path(table_name)
        if not path.exists():
            raise FileNotFoundError(f"Таблица '{table_name}' не существует.")
        records = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key, value in row.items():
                    if key == "id":
                        continue
                    if isinstance(value, str) and value.lstrip("-").isdigit():
                        row[key] = int(value)
                records.append(row)
        return records

    def _save_records(self, table_name: str, records: list[Record]) -> None:
        if not records:
            schema = self._load_schema(table_name)
            columns = schema["columns"]
            path = self._get_csv_path(table_name)
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
        else:
            columns = list(records[0].keys())
            path = self._get_csv_path(table_name)
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(records)

    def create_table(self, table_name: str, columns: Optional[list[str]] = None) -> None:
        if self._get_csv_path(table_name).exists():
            raise ValueError(f"Таблица '{table_name}' уже существует.")
        if columns is None:
            columns = ["id", "brand", "price", "color"]
        self._save_schema(table_name, 1, columns)
        self._save_records(table_name, [])

    def drop_table(self, table_name: str) -> None:
        csv_path = self._get_csv_path(table_name)
        schema_path = self._get_schema_path(table_name)
        if not csv_path.exists():
            raise FileNotFoundError(f"Таблица '{table_name}' не существует.")
        os.remove(csv_path)
        os.remove(schema_path)

    def get_table_names(self) -> list[str]:
        return [p.stem for p in self.data_dir.glob("*.csv")]

    def create_record(self, table_name: str, data: Record) -> Record:
        schema = self._load_schema(table_name)
        next_id = schema["next_id"]
        record = {"id": str(next_id), **data}
        records = self._load_records(table_name)
        records.append(record)
        self._save_records(table_name, records)
        schema["next_id"] = next_id + 1
        self._save_schema(table_name, schema["next_id"], schema["columns"])
        record["id"] = next_id
        return record

    def read_records(self, table_name: str, filters: Optional[Record] = None) -> list[Record]:
        records = self._load_records(table_name)
        for rec in records:
            if "id" in rec and isinstance(rec["id"], str) and rec["id"].isdigit():
                rec["id"] = int(rec["id"])
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
                elif str(rec_val) != str(val):
                    match = False
                    break
            if match:
                filtered.append(rec)
        return filtered

    def update_records(self, table_name: str, filters: Optional[Record], new_data: Record) -> int:
        to_update = self.read_records(table_name, filters)
        if not to_update:
            return 0
        ids_to_update = {str(rec["id"]) for rec in to_update}
        all_records = self._load_records(table_name)
        updated = 0
        for rec in all_records:
            if rec["id"] in ids_to_update:
                for k, v in new_data.items():
                    if k != "id":
                        rec[k] = v
                updated += 1
        self._save_records(table_name, all_records)
        return updated

    def delete_records(self, table_name: str, filters: Optional[Record]) -> int:
        to_delete = self.read_records(table_name, filters)
        if not to_delete:
            return 0
        ids_to_delete = {str(rec["id"]) for rec in to_delete}
        all_records = self._load_records(table_name)
        new_records = [rec for rec in all_records if rec["id"] not in ids_to_delete]
        deleted = len(all_records) - len(new_records)
        self._save_records(table_name, new_records)
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

        def sort_key(rec: Record):
            val = rec.get(key)
            if val is None:
                return default_value
            return val
        try:
            return sorted(records, key=sort_key, reverse=reverse)
        except TypeError as e:
            raise TypeError(f"Ошибка сортировки: {e}")