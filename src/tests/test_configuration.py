import unittest
import mock
import warnings
import os
from automation_of_work_for_stepic import configuration as conf


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)

    return do_test


class TestLoadConfiguration(unittest.TestCase):
    """
    Класс тестирующий load_config
    """

    @ignore_warnings
    def test_init_positive(self):
        """
        Позитивный тест
        Корректное значение данных конфигурации
        """
        config = conf.Configuration()
        conf.Configuration.__init__(config, os.path.join("tests", "resources", "config.json"))
        correct_data_config = {'google_table': {'URL': 'https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', 'Sheet': 0, 'FIO_Col': 1, 'FIO_Rows': [11, 21], 'ID_Col': 5, 'ID_Rows': [11, 21]}, 'stepic': {'id_course': [64]}}
        self.assertEqual(config.get_data(), correct_data_config)

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_wrong_path_config(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если пользователь указал не верный путь к конфигурационному файлу
        """
        config = conf.Configuration()
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("resources", "wrong_path.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Указанного пути не существует, path='resources\wrong_path.json'")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("my_resources", "config.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Указанного пути не существует, path='my_resources\config.json'")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("windows", "config.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Указанного пути не существует, path='windows\config.json'")


    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_decode_error_config(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если конфигурационный файл содержит ошибку json
        """
        config = conf.Configuration()
        config.path = os.path.join("tests", "resources", "empty_file.json")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("tests", "resources", "empty_file.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Ошибка в конфигурационном файле")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("tests", "resources", "config_decode_error_1.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Ошибка в конфигурационном файле")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("tests", "resources", "config_decode_error_2.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Ошибка в конфигурационном файле")
        with self.assertRaises(ValueError) as raised_exception:
            config.path = os.path.join("tests", "resources", "config_decode_error_3.json")
            config.load_config()
        self.assertEqual(raised_exception.exception.args[0], "Ошибка в конфигурационном файле")


class TestGetConfig(unittest.TestCase):
    """
    Класс тестирующий get_config*
    """

    @ignore_warnings
    def test_get_by_key_positive(self):
        """
        Позитивный тест
        Корректное значение конфигурации по ключу
        """
        config = conf.Configuration()
        config.path = os.path.join("tests", "resources", "config.json")
        config.load_config()
        correct_google = {'URL': 'https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', 'Sheet': 0, 'FIO_Col': 1, 'FIO_Rows': [11, 21], 'ID_Col': 5, 'ID_Rows': [11, 21]}
        correct_stepic = {'id_course': [64]}
        self.assertEqual(config.get_google_table_config(), correct_google)
        self.assertEqual(config.get_config_by_key('google_table'), correct_google)
        self.assertEqual(config.get_stepic_config(), correct_stepic)
        self.assertEqual(config.get_config_by_key('stepic'), correct_stepic)

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_empty_data(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если конфигурационные данные пусты
        """
        config = conf.Configuration()
        config.path = os.path.join("tests", "resources", "config_empty.json")
        config.load_config()
        with self.assertRaises(ValueError) as raised_exception:
            config.get_google_table_config()
        self.assertEqual(raised_exception.exception.args[0], "Конфигурационные данные отсутствуют")
        with self.assertRaises(ValueError) as raised_exception:
            config.get_stepic_config()
        self.assertEqual(raised_exception.exception.args[0], "Конфигурационные данные отсутствуют")
        with self.assertRaises(ValueError) as raised_exception:
            config.get_config_by_key('stepic')
        self.assertEqual(raised_exception.exception.args[0], "Конфигурационные данные отсутствуют")
        with self.assertRaises(ValueError) as raised_exception:
            config.get_config_by_key('google_table')
        self.assertEqual(raised_exception.exception.args[0], "Конфигурационные данные отсутствуют")

    @ignore_warnings
    @mock.patch('sys.stderr')
    def test_invalid_key(self, mock_):
        """
        Негативный тест
        Проверяет исключение, если запрашиваются данные по недействительному ключу
        """
        config = conf.Configuration()
        config.path = os.path.join("tests", "resources", "config.json")
        config.load_config()
        with self.assertRaises(ValueError) as raised_exception:
            config.get_config_by_key('key')
        self.assertEqual(raised_exception.exception.args[0], "Ключ недействителен: 'key'")
        with self.assertRaises(ValueError) as raised_exception:
            config.get_config_by_key('ctepic')
        self.assertEqual(raised_exception.exception.args[0], "Ключ недействителен: 'ctepic'")
        with self.assertRaises(ValueError) as raised_exception:
            config.get_config_by_key('googleTable')
        self.assertEqual(raised_exception.exception.args[0], "Ключ недействителен: 'googleTable'")


if __name__ == '__main__':
    unittest.main()
