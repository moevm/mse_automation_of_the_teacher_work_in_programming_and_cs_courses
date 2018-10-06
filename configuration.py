import json


class Configuration:
    _Data = {}

    def __init__(self):
        """
        Считывание конфигурационного файла
        :return: -
        """
        with open('resources/config.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        self._Data = data

    def get_data(self):
        """
        Геттер данных конфигурации
        :return: {} - все данные конфигурации
        """
        return self._Data

    def get_config_by_key(self, key):
        """
        Геттер элемента конфигурации по ключу
        :param key: string - ключ
        :return: элемент конфигурации
        """
        return self._Data[key]


if __name__ == "__main__":
    config = Configuration()
    print(config)
