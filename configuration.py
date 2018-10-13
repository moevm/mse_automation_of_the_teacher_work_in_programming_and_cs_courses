import json
import os


class Configuration:
    _Data = {}

    def __init__(self, path_config_file="resources/config.json"):
        """
        Считывание конфигурационного файла
        :return: -
        """
        if os.path.exists(path_config_file) is True:
            with open(path_config_file, 'r', encoding='utf-8') as fh:
                try:
                    data = json.load(fh)
                except json.decoder.JSONDecodeError:
                    print("Ошибка в конфигурационном файле")
                else:
                    self._Data = data
        else:
            print("Указанного пути не существует")

    def get_data(self):
        """
        Геттер конфигурационных данных
        :return: {} - все данные конфигурации
        """
        return self._Data

    def get_google_table_config(self):
        """
        Геттер конфигурационных данных о google-таблице
        :return: {} - все данные конфигурации, относящиеся к google-таблице
        """
        return self.get_config_by_key("google_table")

    def get_stepic_config(self):
        """
        Геттер конфигурационных данных о stepic
        :return: {} - все данные конфигурации, относящиеся к stepic
        """
        return self.get_config_by_key("stepic")

    def get_config_by_key(self, key):
        """
        Геттер элемента конфигурации по ключу
        :param key: string - ключ
        :return: элемент конфигурации
        """
        if self.is_data_empty() is False:
            if self.is_key_valid(key) is True:
                return self._Data[key]
            else:
                print(f"Ключ недействителен: '{key}'")
        else:
            print("Конфигурационные данные отсутствуют")

    def is_key_valid(self, key):
        """
        Проверка действительности ключа
        :param key: string - ключ
        :return: True - если ключ действителен(присутствует в словаре)
        """
        return key in self._Data.keys()

    def is_data_empty(self):
        """
        Проверка конфигурационных данных на пустоту
        :return: True - если данные отсутствуют, т.е. _Data = {}
        """
        return len(self._Data) == 0


if __name__ == "__main__":
    config = Configuration()
    print(config.get_data())
    print(config.get_google_table_config())
    print(config.get_config_by_key('stepic'))
