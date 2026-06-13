import unittest
import tempfile
import json
from src.db.backend.csv_file import CsvFileDatabase

class TestCsvFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = CsvFileDatabase(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_table(self):
        self.db.create_table("test")
        self.assertIn("test", self.db.get_table_names())
        self.db.drop_table("test")
        self.assertNotIn("test", self.db.get_table_names())

    def test_create_table_already_exists(self):
        self.db.create_table("test")
        with self.assertRaises(ValueError):
            self.db.create_table("test")

    def test_drop_table_not_exists(self):
        with self.assertRaises(FileNotFoundError):
            self.db.drop_table("nonexistent")

    def test_create_record(self):
        self.db.create_table("cars")
        rec = self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})
        self.assertEqual(rec["id"], 1)
        self.assertEqual(rec["brand"], "Toyota")
        self.assertEqual(rec["price"], 20000)

        rec2 = self.db.create_record("cars", {"brand": "BMW", "price": 35000})
        self.assertEqual(rec2["id"], 2)

    def test_read_records_no_filters(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Audi"})
        self.db.create_record("cars", {"brand": "BMW"})
        all_rec = self.db.read_records("cars")
        self.assertEqual(len(all_rec), 2)

    def test_read_records_with_filters(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Audi", "price": 30000})
        self.db.create_record("cars", {"brand": "BMW", "price": 40000})
        result = self.db.read_records("cars", {"brand": "Audi"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["brand"], "Audi")

    def test_read_records_filter_case_insensitive(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota"})
        result = self.db.read_records("cars", {"brand": "toyota"})
        self.assertEqual(len(result), 1)

    def test_update_records(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Old", "price": 100})
        updated = self.db.update_records("cars", {"brand": "Old"}, {"brand": "New", "price": 200})
        self.assertEqual(updated, 1)
        record = self.db.read_records("cars", {"brand": "New"})[0]
        self.assertEqual(record["price"], 200)

    def test_update_no_match(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Old"})
        updated = self.db.update_records("cars", {"brand": "Nonexistent"}, {"brand": "X"})
        self.assertEqual(updated, 0)

    def test_delete_records(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "ToDelete"})
        deleted = self.db.delete_records("cars", {"brand": "ToDelete"})
        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.db.read_records("cars")), 0)

    def test_delete_no_match(self):
        self.db.create_table("cars")
        deleted = self.db.delete_records("cars", {"brand": "Nonexistent"})
        self.assertEqual(deleted, 0)

    def test_sort_records_asc(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"price": 300})
        self.db.create_record("cars", {"price": 100})
        self.db.create_record("cars", {"price": 200})
        sorted_cars = self.db.sort_records("cars", "price")
        prices = [c["price"] for c in sorted_cars]
        self.assertEqual(prices, [100, 200, 300])

    def test_sort_records_desc(self):
        self.db.create_table("cars")
        self.db.create_record("cars", {"price": 100})
        self.db.create_record("cars", {"price": 300})
        sorted_cars = self.db.sort_records("cars", "price", reverse=True)
        prices = [c["price"] for c in sorted_cars]
        self.assertEqual(prices, [300, 100])

    def test_persistence(self):
        self.db.create_table("students")
        self.db.create_record("students", {"name": "Ivan", "age": 20})
        db2 = CsvFileDatabase(self.temp_dir.name)
        records = db2.read_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Ivan")
        self.assertEqual(records[0]["age"], 20)

    def test_schema_file_created(self):
        self.db.create_table("test")
        schema_path = self.temp_dir.name + "/test.schema.json"
        with open(schema_path, "r") as f:
            schema = json.load(f)
        self.assertEqual(schema["columns"], ["id", "brand", "price", "color"])
        self.assertEqual(schema["next_id"], 1)

    def test_csv_file_created_with_header(self):
        self.db.create_table("test")
        csv_path = self.temp_dir.name + "/test.csv"
        with open(csv_path, "r") as f:
            first_line = f.readline().strip()
        self.assertEqual(first_line, "id,brand,price,color")

if __name__ == "__main__":
    unittest.main()