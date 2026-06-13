from typing import Any, Optional
from collections import defaultdict
from .memory import Database as MemoryDatabase
from .errors import TableNotFoundError

Record = dict[str, Any]

class IndexedMemoryDatabase(MemoryDatabase):
    def __init__(self) -> None:
        super().__init__()
        self._indices: dict[str, dict[str, dict[Any, list[int]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    def _rebuild_index(self, table_name: str, field: str) -> None:
        if table_name not in self._tables:
            return
        self._indices[table_name][field] = defaultdict(list)
        for record in self._tables[table_name].values():
            value = record.get(field)
            if value is not None:
                self._indices[table_name][field][value].append(record["id"])

    def create_index(self, table_name: str, field: str) -> None:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        self._rebuild_index(table_name, field)

    def drop_index(self, table_name: str, field: str) -> None:
        if table_name in self._indices and field in self._indices[table_name]:
            del self._indices[table_name][field]

    def _update_index_after_insert(self, table_name: str, record: Record) -> None:
        record_id = record["id"]
        for field, idx_dict in self._indices.get(table_name, {}).items():
            value = record.get(field)
            if value is not None:
                idx_dict[value].append(record_id)

    def _update_index_after_delete(self, table_name: str, record: Record) -> None:
        record_id = record["id"]
        for field, idx_dict in self._indices.get(table_name, {}).items():
            value = record.get(field)
            if value is not None and value in idx_dict and record_id in idx_dict[value]:
                idx_dict[value].remove(record_id)
                if not idx_dict[value]:
                    del idx_dict[value]

    def create_record(self, table_name: str, data: Record) -> Record:
        record = super().create_record(table_name, data)
        self._update_index_after_insert(table_name, record)
        return record

    def update_records(self, table_name: str, filters: Optional[Record], new_data: Record) -> int:
        count = super().update_records(table_name, filters, new_data)
        for field in list(self._indices.get(table_name, {}).keys()):
            self._rebuild_index(table_name, field)
        return count

    def delete_records(self, table_name: str, filters: Optional[Record]) -> int:
        to_delete = self.read_records(table_name, filters)
        count = super().delete_records(table_name, filters)
        for rec in to_delete:
            self._update_index_after_delete(table_name, rec)
        return count

    def read_records(self, table_name: str, filters: Optional[Record] = None) -> list[Record]:
        if filters and len(filters) == 1:
            field, value = next(iter(filters.items()))
            if table_name in self._indices and field in self._indices[table_name]:
                ids = self._indices[table_name][field].get(value, [])
                if ids:
                    table = self._tables[table_name]
                    return [record for record in table.values() if record["id"] in ids]
        return super().read_records(table_name, filters)