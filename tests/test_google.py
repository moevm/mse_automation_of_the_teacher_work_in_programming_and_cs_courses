import unittest
import warnings
import mock
from google import google_table as g_table


class TestInitGoogleTable(unittest.TestCase):
    """
    Класс, тестирующий __init__ GoogleTable
    """

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)

        return do_test

    @ignore_warnings
    def test_init_positive(self):
        """
        Позитивный тест
        Корректное создание объекта GoogleTable
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        self.assertEqual(type(table), g_table.GoogleTable)
        self.assertNotEqual(table.Table, None)
        self.assertNotEqual(table.Sheet, None)


    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_no_valid_url_key(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если ссылка не имеет ключа гугл-таблицы
        """
        t1 = g_table.GoogleTable('https://vk.com')
        t2 = g_table.GoogleTable('https://yandex.ru')
        t3 = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/')
        self.assertEqual(t1.Table, None)
        self.assertEqual(t1.Sheet, None)
        self.assertEqual(t2.Table, None)
        self.assertEqual(t2.Sheet, None)
        self.assertEqual(t3.Table, None)
        self.assertEqual(t3.Sheet, None)

        mock_stdout.write.assert_has_calls([
            mock.call("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу"),
            mock.call('\n'),
            mock.call("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу"),
            mock.call('\n'),
            mock.call("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу"),
            mock.call('\n')
        ])

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_invalid_url_key(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если ссылка имеет не корректный ключ гугл-таблицы
        """
        t1 = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/it_is_wrong_key', 0)
        t2 = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/16I1mG_kMug_test_Bpnh_K23V_GTOWuN5hAEQG6OfOhIOlprA', 1)
        t3 = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/must_be_valid_url', 2)
        self.assertEqual(t1.Table, None)
        self.assertEqual(t1.Sheet, None)
        self.assertEqual(t2.Table, None)
        self.assertEqual(t2.Sheet, None)
        self.assertEqual(t3.Table, None)
        self.assertEqual(t3.Sheet, None)

        mock_stdout.write.assert_has_calls([
            mock.call("Ошибка google_api, проверьте правильность ссылки на таблицу"),
            mock.call('\n'),
            mock.call("Ошибка google_api, проверьте правильность ссылки на таблицу"),
            mock.call('\n'),
            mock.call("Ошибка google_api, проверьте правильность ссылки на таблицу"),
            mock.call('\n')
        ])


class TestSetSheet(unittest.TestCase):
    """
    Класс, тестирующий метод GoogleTable.set_sheet()
    """

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)

        return do_test

    @ignore_warnings
    def test_set_sheet(self):
        """
        Позитивный тест
        Корректное установка листа таблицы
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        self.assertEqual(table.Sheet.title, "Лист №1")
        table.set_sheet(1)
        self.assertEqual(table.Sheet.title, "Лист2")
        table.set_sheet(2)
        self.assertEqual(table.Sheet.title, "Лист3")

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_worksheet_not_found(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если указанного для установки листа не существует
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', "First List")
        self.assertEqual(table.Sheet, None)
        table.set_sheet("Wrong name")
        self.assertEqual(table.Sheet, None)
        table.set_sheet(9999)
        self.assertEqual(table.Sheet, None)
        table.set_sheet(-5555)
        self.assertEqual(table.Sheet, None)

        mock_stdout.write.assert_has_calls([
            mock.call("Несуществующий лист таблицы с именем 'First List'"),
            mock.call('\n'),
            mock.call("Несуществующий лист таблицы с именем 'Wrong name'"),
            mock.call('\n'),
            mock.call("Несуществующий лист таблицы №9999"),
            mock.call('\n'),
            mock.call("Несуществующий лист таблицы №-5555"),
            mock.call('\n')
        ])

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_incorrect_argument_type(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если подан аргумент неверного типа
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', 1.5)
        self.assertEqual(table.Sheet, None)
        table.set_sheet(None)
        self.assertEqual(table.Sheet, None)
        table.set_sheet(True)
        self.assertEqual(table.Sheet, None)
        table.set_sheet(["name"])
        self.assertEqual(table.Sheet, None)
        table.set_sheet({"name": "name"})
        self.assertEqual(table.Sheet, None)

        mock_stdout.write.assert_has_calls([
            mock.call("Неверный формат sheet: 1.5"),
            mock.call('\n'),
            mock.call("Неверный формат sheet: None"),
            mock.call('\n'),
            mock.call("Неверный формат sheet: True"),
            mock.call('\n'),
            mock.call("Неверный формат sheet: ['name']"),
            mock.call('\n'),
            mock.call("Неверный формат sheet: {'name': 'name'}"),
            mock.call('\n')
        ])


class TestGet(unittest.TestCase):
    """
    Класс, тестирующий методы GoogleTable.get*
    """

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)

        return do_test

    @ignore_warnings
    def test_get(self):
        """
        Позитивный тест
        Корректное получение данных из таблицы
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU')
        self.assertEqual(table.get_row(1), ['ФИО', 'ID'])
        self.assertEqual(table.get_list(1, 1, 10), ['Азаревич Артём', 'Афийчук И.И.', 'Гомонова Анастасия ', 'Григорьев И.С.', 'Иванов В.С.', 'Кухарев М.А.', 'Лавренкова Екатерина', 'Мейзер Д.В.', 'Михайлов Ю.А.'])

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_none_sheet(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если вызывается get* при Sheet == None
        """
        table = g_table.GoogleTable('https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', "Non-existent sheet")
        self.assertEqual(table.get_column(1), None)
        self.assertEqual(table.get_row(1), None)
        self.assertEqual(table.get_list(1, 1, 10), None)


if __name__ == '__main__':
    unittest.main()
