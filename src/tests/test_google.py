import unittest
import warnings
import mock

import automation_of_work_for_stepic.google_table as g_table


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)

    return do_test


class TestInitGoogleTable(unittest.TestCase):
    """
    Класс, тестирующий __init__ GoogleTable
    """

    @ignore_warnings
    def test_init_positive(self):
        """
        Позитивный тест
        Корректное создание объекта GoogleTable
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        self.assertEqual(type(table), g_table.GoogleTable().__class__)
        self.assertNotEqual(table.Table, None)
        self.assertNotEqual(table.Sheet, None)

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_no_valid_url_key(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если ссылка не имеет ключа гугл-таблицы
        """
        table = g_table.GoogleTable()
        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://vk.com')
        self.assertEqual(raised_exception.exception.args[0],
                         "Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://yandex.ru')
        self.assertEqual(raised_exception.exception.args[0],
                         "Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://docs.google.com/spreadsheets/d/')
        self.assertEqual(raised_exception.exception.args[0],
                         "Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_invalid_url_key(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если ссылка имеет не корректный ключ гугл-таблицы
        """
        table = g_table.GoogleTable()
        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://docs.google.com/spreadsheets/d/it_is_wrong_key')
        self.assertEqual(raised_exception.exception.args[0],
                         "Ошибка google_api, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://docs.google.com/spreadsheets/d/16I1mG_kMug_test_Bpnh_K23V_GTOWuN5hAEQG6OfOhIOlprA')
        self.assertEqual(raised_exception.exception.args[0],
                         "Ошибка google_api, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_table('https://docs.google.com/spreadsheets/d/must_be_valid_url')
        self.assertEqual(raised_exception.exception.args[0],
                         "Ошибка google_api, проверьте правильность ссылки на таблицу")
        self.assertEqual(table.Table, None)
        self.assertEqual(table.Sheet, None)


class TestSetSheet(unittest.TestCase):
    """
    Класс, тестирующий метод GoogleTable.set_sheet()
    """

    @ignore_warnings
    def test_set_sheet(self):
        """
        Позитивный тест
        Корректное установка листа таблицы
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        table.set_sheet("Лист №1")
        self.assertEqual(table.Sheet.title, "Лист №1")
        table.set_sheet(1)
        self.assertEqual(table.Sheet.title, "Лист2")
        table.set_sheet(2)
        self.assertEqual(table.Sheet.title, "Лист3")

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_worksheet_not_found(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если указанного для установки листа не существует
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet("First List")
        self.assertEqual(raised_exception.exception.args[0], "Несуществующий лист таблицы с именем 'First List'")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet("Wrong name")
        self.assertEqual(raised_exception.exception.args[0], "Несуществующий лист таблицы с именем 'Wrong name'")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(9999)
        self.assertEqual(raised_exception.exception.args[0], "Несуществующий лист таблицы №9999")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(-5555)
        self.assertEqual(raised_exception.exception.args[0], "Несуществующий лист таблицы №-5555")
        self.assertEqual(table.Sheet, None)

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_incorrect_argument_type(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если подан аргумент неверного типа
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(1.5)
        self.assertEqual(raised_exception.exception.args[0], "Неверный формат sheet: 1.5")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(None)
            self.assertEqual(raised_exception.exception.args[0], "Неверный формат sheet: None")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(True)
            self.assertEqual(raised_exception.exception.args[0], "Неверный формат sheet: True")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet(["name"])
            self.assertEqual(raised_exception.exception.args[0], "Неверный формат sheet: ['name']")
        self.assertEqual(table.Sheet, None)

        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet({"name": "name"})
            self.assertEqual(raised_exception.exception.args[0], "Неверный формат sheet: {'name': 'name'}")
        self.assertEqual(table.Sheet, None)


class TestGet(unittest.TestCase):
    """
    Класс, тестирующий методы GoogleTable.get*
    """

    @ignore_warnings
    def test_get(self):
        """
        Позитивный тест
        Корректное получение данных из таблицы
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        self.assertEqual(table.get_row(1), ['ФИО', 'ID'])
        self.assertEqual(table.get_list(1, 2, 11),
                         ['Азаревич Артём', 'Афийчук И.И.', 'Гомонова Анастасия ', 'Григорьев И.С.', 'Иванов В.С.',
                          'Кухарев М.А.', 'Лавренкова Екатерина', 'Мейзер Д.В.', 'Михайлов Ю.А.'])

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_none_sheet(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если вызывается get* при Sheet == None
        """
        table = g_table.GoogleTable()
        table.set_table('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        with self.assertRaises(ValueError) as raised_exception:
            table.set_sheet("Non-existent sheet")
        self.assertEqual(raised_exception.exception.args[0],
                         "Несуществующий лист таблицы с именем 'Non-existent sheet'")
        self.assertEqual(table.get_column(1), None)
        self.assertEqual(table.get_row(1), None)
        self.assertEqual(table.get_list(1, 1, 10), None)


if __name__ == '__main__':
    unittest.main()
