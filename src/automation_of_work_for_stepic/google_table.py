import os

from oauth2client.service_account import ServiceAccountCredentials
import gspread.exceptions


from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic.utility import singleton
import logging


@singleton
class GoogleTable:
    Table = None
    Sheet = None

    def __init__(self, key_path=os.path.join("private key for GoogleAPI.json")):
        """
        :param url: string - ссылка на таблицу
        :param sheet: int/string - номер/название листа таблицы
        :param key_path: путь к токену для работы с google_api
        """
        if os.path.exists(key_path):
            self.gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name(key_path, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']))
            self.Table=None
        else:
            logging.error("Указанного пути к токену google_api не существует")

    def set_table(self,url, sheet=0):
        """
        Установка параметров таблицы
        :param url: string - ссылка на таблицу
        :param sheet: int/string - номер/название листа таблицы
        :return: None
        """
        try:
            self.Table = self.gc.open_by_url(url)
        except gspread.exceptions.NoValidUrlKeyFound:
            logging.error("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        else:
            try:
                self.set_sheet(sheet)
            except gspread.exceptions.APIError:
                self.Table = None
                logging.error("Ошибка google_api, проверьте правильность ссылки на таблицу")

    def set_sheet(self, sheet):
        """
        Сеттер текущего листа таблицы
        :param sheet: int/string - номер/название листа таблицы
        :return: -
        """
        if not self.Table:
            self.Sheet = None
            return

        if type(sheet) is int:
            self.Sheet = self.Table.get_worksheet(sheet)
            if not self.Sheet:
                logging.warning(f"Несуществующий лист таблицы №{sheet}")
        elif type(sheet) is str:
            try:
                self.Sheet = self.Table.worksheet(sheet)
            except gspread.exceptions.WorksheetNotFound:
                self.Sheet = None
                logging.warning(f"Несуществующий лист таблицы с именем '{sheet}'")
        else:
            logging.warning(f"Неверный формат sheet: {sheet}")

    def get_column(self, num):
        """
        Геттер столбца
        :param num: int - номер требуемого столбца
        :return: [] - список значений всех ячеек столбца
        """
        if self.Sheet:
            return self.Sheet.col_values(num)

    def get_row(self, num):
        """
        Геттер строки
        :param num: int - номер требуемой строки
        :return: [] - список значений всех ячеек строки
        """
        if self.Sheet:
            return self.Sheet.row_values(num)

    def get_list(self, col, row_from, row_to):
        """
        Геттер списка строк столбца из заданного диапазона
        :param col: int - номер столбца
        :param row_from: int -начало диапазона строк
        :param row_to: int -конец диапазона строк
        :return: [] - список значений ячеек требуемого диапазона строк из столбца
        """
        if self.Sheet:
            return self.get_column(col)[row_from-1:row_to-1]


if __name__ == "__main__":
    'Создание(чтение) конфигурации'
    config = conf.Configuration()
    'Получение конфигурационных данных о гугл-таблице'
    table_config = config.get_google_table_config()
    'Открытие таблицы с помощью gspread согласно конфигурационным данным'
    a = GoogleTable()
    a.set_table(table_config['URL'], table_config['Sheet'])
    'Получение списка из таблицы'
    print(a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0], table_config['FIO_Rows'][1]))
    print(a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0], table_config['ID_Rows'][1]))
