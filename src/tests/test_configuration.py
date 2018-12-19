import unittest
import mock
import warnings
import os
from automation_of_work_for_stepic import configuration as conf


class TestInitConfiguration(unittest.TestCase):
    """
    Класс тестирующий __init__
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
        Корректное значение данных конфигурации
        """
        config = conf.Configuration()
        conf.Configuration.__init__(config, os.path.join("tests", "resources", "config.json"))
        correct_data_config = {'google_table': {'URL': 'https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', 'Sheet': 0, 'FIO_Col': 1, 'FIO_Rows': [11, 21], 'ID_Col': 5, 'ID_Rows': [11, 21]}, 'stepic': {'id_course': [64]}}
        self.assertEqual(config.get_data(), correct_data_config)

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_wrong_path_config(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если пользователь указал не верный путь к конфигурационному файлу
        """
        conf.Configuration.__init__(conf.Configuration(),os.path.join("resources", "wrong_path.json"))
        conf.Configuration.__init__(conf.Configuration(), os.path.join("config.json"))
        conf.Configuration.__init__(conf.Configuration(), os.path.join("windows", "config.json"))
        mock_stdout.write.assert_has_calls([
            mock.call("Указанного пути не существует"),
            mock.call('\n'),
            mock.call("Указанного пути не существует"),
            mock.call('\n'),
            mock.call("Указанного пути не существует"),
            mock.call('\n')
        ])

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_decode_error_config(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если конфигурационный файл содержит ошибку json
        """
        conf.Configuration.__init__(conf.Configuration(),os.path.join("tests", "resources", "empty_file.json"))
        conf.Configuration.__init__(conf.Configuration(),os.path.join("tests", "resources", "config_decode_error_1.json"))
        conf.Configuration.__init__(conf.Configuration(),os.path.join("tests", "resources", "config_decode_error_2.json"))
        conf.Configuration.__init__(conf.Configuration(),os.path.join("tests", "resources", "config_decode_error_3.json"))
        mock_stdout.write.assert_has_calls([
            mock.call("Ошибка в конфигурационном файле"),
            mock.call('\n'),
            mock.call("Ошибка в конфигурационном файле"),
            mock.call('\n'),
            mock.call("Ошибка в конфигурационном файле"),
            mock.call('\n'),
            mock.call("Ошибка в конфигурационном файле"),
            mock.call('\n'),
        ])


class TestGetConfig(unittest.TestCase):
    """
    Класс тестирующий get_config*
    """

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)

        return do_test

    @ignore_warnings
    def test_get_by_key_positive(self):
        """
        Позитивный тест
        Корректное значение конфигурации по ключу
        """
        config = conf.Configuration()
        conf.Configuration.__init__(config, os.path.join("tests", "resources", "config.json"))
        correct_google = {'URL': 'https://docs.google.com/spreadsheets/d/1t1szRuyb023sfuXLf6p-fDLmMcNtAmKfK0enj4URTxU', 'Sheet': 0, 'FIO_Col': 1, 'FIO_Rows': [11, 21], 'ID_Col': 5, 'ID_Rows': [11, 21]}
        correct_stepic = {'id_course': [64]}
        self.assertEqual(config.get_google_table_config(), correct_google)
        self.assertEqual(config.get_config_by_key('google_table'), correct_google)
        self.assertEqual(config.get_stepic_config(), correct_stepic)
        self.assertEqual(config.get_config_by_key('stepic'), correct_stepic)

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_empty_data(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если конфигурационные данные пусты
        """
        config = conf.Configuration()
        conf.Configuration.__init__(config, os.path.join("tests", "resources", "config_empty.json"))
        config.get_google_table_config()
        config.get_stepic_config()
        config.get_config_by_key('stepic')
        config.get_config_by_key('google_table')
        mock_stdout.write.assert_has_calls([
            mock.call("Конфигурационные данные отсутствуют"),
            mock.call('\n'),
            mock.call("Конфигурационные данные отсутствуют"),
            mock.call('\n'),
            mock.call("Конфигурационные данные отсутствуют"),
            mock.call('\n'),
            mock.call("Конфигурационные данные отсутствуют"),
            mock.call('\n'),
        ])

    @ignore_warnings
    @mock.patch('sys.stdout')
    def test_invalid_key(self, mock_stdout):
        """
        Негативный тест
        Проверяет исключение, если запрашиваются данные по недействительному ключу
        """
        config = conf.Configuration()
        conf.Configuration.__init__(config, os.path.join("tests", "resources", "config.json"))
        config.get_config_by_key('key')
        config.get_config_by_key('ctepic')
        config.get_config_by_key('googleTable')
        mock_stdout.write.assert_has_calls([
            mock.call("Ключ недействителен: 'key'"),
            mock.call('\n'),
            mock.call("Ключ недействителен: 'ctepic'"),
            mock.call('\n'),
            mock.call("Ключ недействителен: 'googleTable'"),
            mock.call('\n'),
        ])


if __name__ == '__main__':
    unittest.main()
