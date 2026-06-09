import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import CarDatabaseUI
from src.db.backend.memory import Database


class TestCarDatabaseUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Один раз создаём БД и UI для всех тестов."""
        cls.db = Database()
        cls.ui = CarDatabaseUI()
        cls.ui.db = cls.db
        cls.db.create_table("cars")
        cls.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})

    def test_get_non_empty(self):
        with patch('builtins.input', return_value="  BMW  "):
            val = self.ui._get_non_empty("Enter: ")
        self.assertEqual(val, "BMW")


    def test_get_int(self):
        with patch('builtins.input', return_value="15000"):
            val = self.ui._get_int("Price: ")
        self.assertEqual(val, 15000)

    def test_get_filters(self):
        cases = [
            (["", "", ""], {}),
            (["Toyota", "", ""], {"brand": "Toyota"}),
            (["", "20000", ""], {"price": 20000}),
            (["", "", "red"], {"color": "red"}),
        ]
        for inputs, expected in cases:
            with patch('builtins.input', side_effect=inputs):
                filters = self.ui._get_filters()
                self.assertEqual(filters, expected)

    def test_get_data(self):
        inputs = ["Honda", "18000", "blue"]
        with patch('builtins.input', side_effect=inputs):
            data = self.ui._get_data()
        self.assertEqual(data, {"brand": "Honda", "price": 18000, "color": "blue"})

    def test_print_records(self):
        self.ui._print_records([])
        self.ui._print_records([{"id": 1, "brand": "Audi", "price": 30000, "color": "white"}])

    def test_table_management_create(self):
        with patch('builtins.input', side_effect=["1", "new_table", "0"]):
            self.ui._table_management()
        self.assertIn("new_table", self.db.get_table_names())
        self.db.drop_table("new_table")

    def test_choose_existing_table(self):
        with patch('builtins.input', return_value="cars"):
            with patch.object(self.ui, '_work_with_table') as mock_work:
                self.ui._choose_and_work_with_table()
                mock_work.assert_called_once_with("cars")

    def test_choose_nonexistent_table(self):
        with patch('builtins.input', return_value="wrong"):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._choose_and_work_with_table()
                self.assertIn("Таблица 'wrong' не найдена", mock_out.getvalue())

    def test_sort_table_empty(self):
        self.db.create_table("empty")
        with patch('builtins.input', side_effect=["empty", "price", "n"]):
            self.ui._sort_table()
        self.db.drop_table("empty")

    def test_sort_table_valid(self):
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        with patch('builtins.input', side_effect=["cars", "price", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._sort_table()
                output = mock_out.getvalue()
                self.assertIn("20000", output)
                self.assertIn("30000", output)
                self.assertIn("35000", output)
        self.db.delete_records("cars", {"brand": "Audi"})
        self.db.delete_records("cars", {"brand": "BMW"})

    def test_sort_table_invalid_field(self):
        with patch('builtins.input', side_effect=["cars", "invalid_field", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._sort_table()
                self.assertIn("Недопустимое поле", mock_out.getvalue())

    def test_work_with_table_add(self):
        with patch.object(self.ui, '_get_data', return_value={"brand": "Honda", "price": 18000, "color": "blue"}):
            with patch('builtins.input', side_effect=["1", "0"]):
                self.ui._work_with_table("cars")
        records = self.db.read_records("cars", {"brand": "Honda"})
        self.assertEqual(len(records), 1)
        self.db.delete_records("cars", {"brand": "Honda"})

    def test_work_with_table_find(self):
        filters = {"brand": "Toyota"}
        with patch.object(self.ui, '_get_filters', return_value=filters):
            with patch('builtins.input', side_effect=["2", "0"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_out:
                    self.ui._work_with_table("cars")
                    self.assertIn("Toyota", mock_out.getvalue())

    def test_work_with_table_update(self):
        filters = {"brand": "Toyota"}
        new_data = {"brand": "Lexus", "price": 22000, "color": "silver"}
        with patch.object(self.ui, '_get_filters', return_value=filters):
            with patch.object(self.ui, '_get_data', return_value=new_data):
                with patch('builtins.input', side_effect=["3", "0"]):
                    self.ui._work_with_table("cars")
        old = self.db.read_records("cars", {"brand": "Toyota"})
        new = self.db.read_records("cars", {"brand": "Lexus"})
        self.assertEqual(len(old), 0)
        self.assertEqual(len(new), 1)
        self.db.update_records("cars", {"brand": "Lexus"}, {"brand": "Toyota", "price": 20000, "color": "red"})

    def test_work_with_table_delete(self):
        self.db.create_record("cars", {"brand": "ToDelete", "price": 100, "color": "white"})
        filters = {"brand": "ToDelete"}
        with patch.object(self.ui, '_get_filters', return_value=filters):
            with patch('builtins.input', side_effect=["4", "y", "0"]):
                self.ui._work_with_table("cars")
        remaining = self.db.read_records("cars", {"brand": "ToDelete"})
        self.assertEqual(len(remaining), 0)

    def test_work_with_table_show_all(self):
        with patch('builtins.input', side_effect=["5", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._work_with_table("cars")
                self.assertIn("Toyota", mock_out.getvalue())

    def test_memory_edge_cases(self):
        with self.assertRaises(ValueError):
            self.db.drop_table("no_such")
        updated = self.db.update_records("cars", None, {"color": "green"})
        self.assertGreaterEqual(updated, 1)
        self.db.create_table("empty2")
        self.assertEqual(self.db.sort_records("empty2", "price"), [])
        self.db.drop_table("empty2")
    def test_run_invalid_choice(self):
        with patch('builtins.input', side_effect=["99", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui.run()
                self.assertIn("Неверный ввод", out.getvalue())

    def test_run_management_choice(self):
        with patch('builtins.input', side_effect=["1", "0", "0"]):
            with patch.object(self.ui, '_table_management') as mock:
                self.ui.run()
                mock.assert_called_once()

    def test_run_work_choice(self):
        with patch('builtins.input', side_effect=["2", "0"]):
            with patch.object(self.ui, '_choose_and_work_with_table') as mock:
                self.ui.run()
                mock.assert_called_once()

    def test_run_sort_choice(self):
        with patch('builtins.input', side_effect=["3", "0"]):
            with patch.object(self.ui, '_sort_table') as mock:
                self.ui.run()
                mock.assert_called_once()

    def test_table_management_delete(self):
        self.db.create_table("temp")
        with patch('builtins.input', side_effect=["2", "temp", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._table_management()
                self.assertIn("удалена", out.getvalue())
        self.assertNotIn("temp", self.db.get_table_names())

    def test_choose_no_tables(self):
        self.db.drop_table("cars")
        with patch('builtins.input', return_value="0"):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._choose_and_work_with_table()
                self.assertIn("Нет таблиц", out.getvalue())
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})

    def test_sort_no_tables(self):
        self.db.drop_table("cars")
        with patch('builtins.input', return_value="0"):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._sort_table()
                self.assertIn("Нет таблиц для сортировки", out.getvalue())
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})

    def test_sort_table_not_found(self):
        with patch('builtins.input', side_effect=["missing", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._sort_table()
                self.assertIn("Таблица не найдена", out.getvalue())

    def test_work_with_table_switch(self):
        with patch('builtins.input', return_value="6"):
            result = self.ui._work_with_table("cars")
            self.assertIsNone(result)

    def test_work_with_table_back(self):
        with patch('builtins.input', return_value="0"):
            result = self.ui._work_with_table("cars")
            self.assertIsNone(result)

    def test_work_with_table_invalid(self):
        with patch('builtins.input', side_effect=["99", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._work_with_table("cars")
                self.assertIn("Неверный ввод", out.getvalue())

    def test_get_filters_price_invalid(self):
        with patch('builtins.input', side_effect=["", "abc", ""]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                filters = self.ui._get_filters()
                self.assertEqual(filters, {})
                self.assertIn("пропущен", out.getvalue())

    def test_update_no_match(self):
        with patch.object(self.ui, '_get_filters', return_value={"brand": "NoSuch"}):
            with patch('builtins.input', side_effect=["3", "0"]):
                with patch('sys.stdout', new_callable=StringIO) as out:
                    self.ui._work_with_table("cars")
                    self.assertIn("Нет записей", out.getvalue())

    def test_delete_cancel(self):
        self.db.create_record("cars", {"brand": "ToDel", "price": 0, "color": "x"})
        with patch.object(self.ui, '_get_filters', return_value={"brand": "ToDel"}):
            with patch('builtins.input', side_effect=["4", "n", "0"]):
                with patch('sys.stdout', new_callable=StringIO) as out:
                    self.ui._work_with_table("cars")
                    self.assertIn("Удаление отменено", out.getvalue())
        self.db.delete_records("cars", {"brand": "ToDel"})

if __name__ == "__main__":
    unittest.main()