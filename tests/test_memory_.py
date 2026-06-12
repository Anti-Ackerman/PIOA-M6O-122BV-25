import unittest
from src.db.backend.memory import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})

    def test_create_table_success(self):
        self.db.create_table("new_table")
        self.assertIn("new_table", self.db.get_table_names())

    def test_create_table_duplicate(self):
        with self.assertRaises(ValueError):
            self.db.create_table("cars")

    def test_drop_table_success(self):
        self.db.drop_table("cars")
        self.assertNotIn("cars", self.db.get_table_names())

    def test_drop_table_nonexistent(self):
        with self.assertRaises(ValueError):
            self.db.drop_table("non_existent")

    def test_create_record(self):
        new_car = self.db.create_record("cars", {"brand": "Honda", "price": 18000, "color": "blue"})
        self.assertIn("id", new_car)
        self.assertEqual(new_car["brand"], "Honda")
        all_cars = self.db.read_records("cars")
        self.assertEqual(len(all_cars), 4)

    def test_create_record_invalid_table(self):
        with self.assertRaises(ValueError):
            self.db.create_record("wrong", {"brand": "Fiat"})

    def test_read_records_no_filters(self):
        cars = self.db.read_records("cars")
        self.assertEqual(len(cars), 3)

    def test_read_records_with_filters(self):
        toyota = self.db.read_records("cars", {"brand": "Toyota"})
        self.assertEqual(len(toyota), 1)
        self.assertEqual(toyota[0]["price"], 20000)

        expensive = self.db.read_records("cars", {"price": 35000})
        self.assertEqual(len(expensive), 1)
        self.assertEqual(expensive[0]["brand"], "BMW")

        no_match = self.db.read_records("cars", {"brand": "Lada"})
        self.assertEqual(no_match, [])

    def test_read_records_invalid_table(self):
        with self.assertRaises(ValueError):
            self.db.read_records("no_table")

    def test_update_records(self):
        updated_count = self.db.update_records("cars", {"brand": "Toyota"}, {"price": 22000})
        self.assertEqual(updated_count, 1)
        toyota = self.db.read_records("cars", {"brand": "Toyota"})[0]
        self.assertEqual(toyota["price"], 22000)

    def test_update_records_no_match(self):
        updated_count = self.db.update_records("cars", {"brand": "Lada"}, {"price": 10000})
        self.assertEqual(updated_count, 0)

    def test_delete_records(self):
        deleted_count = self.db.delete_records("cars", {"brand": "BMW"})
        self.assertEqual(deleted_count, 1)
        remaining = self.db.read_records("cars")
        self.assertEqual(len(remaining), 2)

    def test_delete_records_no_match(self):
        deleted_count = self.db.delete_records("cars", {"brand": "Lada"})
        self.assertEqual(deleted_count, 0)

    def test_get_table_names(self):
        names = self.db.get_table_names()
        self.assertIn("cars", names)
        self.db.create_table("another")
        self.assertEqual(len(self.db.get_table_names()), 2)

    def test_sort_records_by_price_asc(self):
        sorted_cars = self.db.sort_records("cars", "price")
        prices = [car["price"] for car in sorted_cars]
        self.assertEqual(prices, [20000, 30000, 35000])

    def test_sort_records_by_price_desc(self):
        sorted_cars = self.db.sort_records("cars", "price", reverse=True)
        prices = [car["price"] for car in sorted_cars]
        self.assertEqual(prices, [35000, 30000, 20000])

    def test_sort_records_by_brand(self):
        sorted_cars = self.db.sort_records("cars", "brand")
        brands = [car["brand"] for car in sorted_cars]
        self.assertEqual(brands, ["Audi", "BMW", "Toyota"])

    def test_sort_records_empty_table(self):
        self.db.create_table("empty")
        result = self.db.sort_records("empty", "price")
        self.assertEqual(result, [])

    def test_sort_records_missing_key(self):
        self.db.create_table("test_missing")
        self.db.create_record("test_missing", {"brand": "A", "price": 100, "color": "red"})
        self.db.create_record("test_missing", {"brand": "B", "price": 200, "color": "blue"})
        sorted_records = self.db.sort_records("test_missing", "year")
        self.assertEqual(len(sorted_records), 2)
        self.db.drop_table("test_missing")

    def test_sort_records_invalid_table(self):
        with self.assertRaises(ValueError):
            self.db.sort_records("nonexistent", "price")

    def test_sort_records_mixed_types_handling(self):
        self.db.create_table("no_year")
        self.db.create_record("no_year", {"brand": "A"})
        self.db.create_record("no_year", {"brand": "B"})
        sorted_records = self.db.sort_records("no_year", "year")
        self.assertEqual(len(sorted_records), 2)

    def test_drop_table_nonexistent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.db.drop_table("no_such_table")

    def test_update_records_with_none_filters(self):
        self.db.create_table("test_update")
        self.db.create_record("test_update", {"brand": "A", "price": 100, "color": "red"})
        self.db.create_record("test_update", {"brand": "B", "price": 200, "color": "blue"})
        updated = self.db.update_records("test_update", None, {"color": "green"})
        self.assertEqual(updated, 2)
        records = self.db.read_records("test_update")
        for rec in records:
            self.assertEqual(rec["color"], "green")
        self.db.drop_table("test_update")

if __name__ == "__main__":
    unittest.main()