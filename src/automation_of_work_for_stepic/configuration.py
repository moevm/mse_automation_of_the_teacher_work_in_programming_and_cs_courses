import json
import os
import logging
from automation_of_work_for_stepic.utility import singleton


@singleton
class Configuration:

    def __init__(self, path_config_file=os.path.join("resources", "config.json")):
        self._Data = None
        self.path = path_config_file  # сохранение пути к конфигурационному файлу для возможности обновления
        self.load_config()

    def load_config(self):
        """
        Считывание конфигурационного файла (путь хранится в self.path)
        :return: -
        """
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as fh:
                try:
                    data = json.load(fh)
                except json.decoder.JSONDecodeError:
                    logging.error("Ошибка в конфигурационном файле")
                    self._Data = None  # в случае ошибки обнуление прошлых данных
                    raise ValueError("Ошибка в конфигурационном файле")
                else:
                    self._Data = data
        else:
            logging.error("Указанного пути не существует, path='%s'", self.path)
            self._Data = None  # в случае ошибки обнуление прошлых данных
            raise ValueError("Указанного пути не существует, path='" + self.path + "'")

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
        if self._Data:
            if key in self._Data:
                return self._Data[key]
            else:
                logging.error("Ключ недействителен: '%s'", key)
                raise ValueError("Ключ недействителен: '" + key + "'")
        else:
            logging.error("Конфигурационные данные отсутствуют")
            raise ValueError("Конфигурационные данные отсутствуют")


if __name__ == "__main__":
    config = Configuration()
    print(config.get_data())
    print(config.get_google_table_config())
    print(config.get_config_by_key('stepic'))
