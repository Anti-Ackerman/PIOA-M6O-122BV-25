import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import CarDatabaseUI
from src.db.backend.memory import Database as MemoryDatabase

class TestCarDatabaseUI(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})
        self.ui = CarDatabaseUI(db_instance=self.db)

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
        ]
        for inputs, expected in cases:
            with patch('builtins.input', side_effect=inputs):
                filters = self.ui._get_filters()
                self.assertEqual(filters, expected)

    def test_get_data(self):
        with patch('builtins.input', side_effect=["Honda", "18000", "blue"]):
            data = self.ui._get_data()
        self.assertEqual(data, {"brand": "Honda", "price": 18000, "color": "blue"})

    def test_print_records_empty(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            self.ui._print_records([])
            self.assertIn("Автомобили не найдены", mock_out.getvalue())

    def test_print_records_non_empty(self):
        records = [{"id": 1, "brand": "Audi", "price": 30000, "color": "white"}]
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            self.ui._print_records(records)
            output = mock_out.getvalue()
            self.assertIn("Audi", output)
            self.assertIn("30000", output)

    def test_table_management_create(self):
        with patch('builtins.input', side_effect=["1", "new_table", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._table_management()
                self.assertIn("Таблица 'new_table' создана", mock_out.getvalue())
        self.assertIn("new_table", self.db.get_table_names())

    def test_table_management_delete(self):
        self.db.create_table("temp")
        with patch('builtins.input', side_effect=["2", "temp", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._table_management()
                self.assertIn("удалена", mock_out.getvalue())
        self.assertNotIn("temp", self.db.get_table_names())

    def test_table_management_show_tables(self):
        self.db.create_table("test1")
        self.db.create_table("test2")
        with patch('builtins.input', side_effect=["3", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._table_management()
                output = mock_out.getvalue()
                self.assertIn("test1", output)
                self.assertIn("test2", output)

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

    def test_work_with_table_add(self):
        with patch('builtins.input', side_effect=["1", "Honda", "18000", "blue", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._work_with_table("cars")
                self.assertIn("Добавлен", mock_out.getvalue())
        records = self.db.read_records("cars", {"brand": "Honda"})
        self.assertEqual(len(records), 1)

    def test_work_with_table_find(self):
        with patch('builtins.input', side_effect=["2", "Toyota", "", "", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._work_with_table("cars")
                self.assertIn("Toyota", mock_out.getvalue())

    def test_work_with_table_update(self):
        with patch('builtins.input', side_effect=[
            "3", "Toyota", "", "", "Lexus", "", "", "0", "0", "0"
        ]):
            self.ui._work_with_table("cars")
        self.assertEqual(len(self.db.read_records("cars", {"brand": "Toyota"})), 0)
        self.assertEqual(len(self.db.read_records("cars", {"brand": "Lexus"})), 1)
        
    def test_work_with_table_delete(self):
        self.db.create_record("cars", {"brand": "ToDelete", "price": 100, "color": "white"})
        with patch('builtins.input', side_effect=["4", "ToDelete", "", "", "y", "0"]):
            self.ui._work_with_table("cars")
        self.assertEqual(len(self.db.read_records("cars", {"brand": "ToDelete"})), 0)

    def test_work_with_table_show_all(self):
        with patch('builtins.input', side_effect=["5", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._work_with_table("cars")
                self.assertIn("Toyota", mock_out.getvalue())

    def test_work_with_table_no_match_update(self):
        with patch('builtins.input', side_effect=["3", "NoSuch", "", "", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._work_with_table("cars")
                self.assertIn("Нет записей", mock_out.getvalue())

    def test_work_with_table_switch(self):
        with patch('builtins.input', side_effect=["6"]):
            self.ui._work_with_table("cars")  

    def test_work_with_table_exit(self):
        with patch('builtins.input', side_effect=["0"]):
            self.ui._work_with_table("cars")

    def test_sort_table_empty(self):
        self.db.create_table("empty")
        with patch('builtins.input', side_effect=["empty", "price", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._sort_table()
                self.assertIn("Таблица пуста", mock_out.getvalue())

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

    def test_sort_table_invalid_field(self):
        with patch('builtins.input', side_effect=["cars", "invalid", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._sort_table()
                self.assertIn("Недопустимое поле", mock_out.getvalue())

    def test_get_filters_price_invalid(self):
        with patch('builtins.input', side_effect=["", "abc", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                filters = self.ui._get_filters()
                self.assertEqual(filters, {})
                self.assertIn("пропущен", mock_out.getvalue().lower())

    def test_run_management_choice(self):
        with patch('builtins.input', side_effect=["1", "0", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui.run()
                self.assertIn("Управление таблицами", mock_out.getvalue())

    def test_run_work_choice(self):
        with patch('builtins.input', side_effect=["2", "cars", "0", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui.run()
                self.assertIn("Работа с таблицей", mock_out.getvalue())

    def test_run_sort_choice(self):
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        with patch('builtins.input', side_effect=["3", "cars", "price", "n", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui.run()
                output = mock_out.getvalue()
                self.assertIn("20000", output)
                self.assertIn("30000", output)
                self.assertIn("35000", output)

    def test_run_invalid_choice(self):
        with patch('builtins.input', side_effect=["99", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui.run()
                self.assertIn("Неверный ввод", mock_out.getvalue())

    def test_sort_table_no_tables(self):
        for table in self.db.get_table_names():
            self.db.drop_table(table)
        with patch('builtins.input', side_effect=["0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._sort_table()
                self.assertIn("Нет таблиц", mock_out.getvalue())

    def test_choose_no_tables(self):
        for table in self.db.get_table_names():
            self.db.drop_table(table)
        with patch('builtins.input', return_value="0"):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                self.ui._choose_and_work_with_table()
                self.assertIn("Нет таблиц", mock_out.getvalue())

if __name__ == "__main__":
    unittest.main()