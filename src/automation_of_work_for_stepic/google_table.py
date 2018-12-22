import os

from oauth2client.service_account import ServiceAccountCredentials
import gspread.exceptions
import gspread.utils

from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic.utility import singleton
import logging


@singleton
class GoogleTable:
    Table = None
    Sheet = None

    def __init__(self, key_path=os.path.join("resources", "private key for GoogleAPI.json")):
        """

        :param key_path: путь к токену для работы с google_api
        """
        if os.path.exists(key_path):
            self.gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name(key_path, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']))
            self.Table = None
        else:
            logging.error("Указанного пути к токену google_api не существует")
            raise ValueError("Указанного пути к токену google_api не существует")

    def set_table(self, url, sheet=0):
        """
        Установка параметров таблицы
        :param url: string - ссылка на таблицу
        :param sheet: int/string - номер/название листа таблицы
        :return: None
        """
        try:
            self.Table = self.gc.open_by_url(url)
        except gspread.exceptions.NoValidUrlKeyFound:
            self.Table = None
            self.Sheet = None
            logging.error("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
            raise ValueError("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        else:
            try:
                self.set_sheet(sheet)
            except gspread.exceptions.APIError:
                self.Table = None
                self.Sheet = None
                logging.error("Ошибка google_api, проверьте правильность ссылки на таблицу")
                raise ValueError("Ошибка google_api, проверьте правильность ссылки на таблицу")

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
            self.Sheet = self.Table.get_worksheet(sheet)  # если лист таблицы задан номером
            if not self.Sheet:
                logging.warning("Несуществующий лист таблицы №%s",sheet)
                raise ValueError("Несуществующий лист таблицы №%s", sheet)
        elif type(sheet) is str:
            try:
                self.Sheet = self.Table.worksheet(sheet)  # если лист таблицы задан именем
            except gspread.exceptions.WorksheetNotFound:
                self.Sheet = None
                logging.warning("Несуществующий лист таблицы с именем '%s'", sheet)
                raise ValueError("Несуществующий лист таблицы с именем '%s'", sheet)
        else:
            self.Sheet = None
            logging.warning("Неверный формат sheet: %s", sheet)
            raise ValueError("Неверный формат sheet: %s", sheet)

    def get_column(self, col):
        """
        Геттер столбца
        :param col: int/str - номер/название требуемого столбца
        :return: [] - список значений всех ячеек столбца
        """
        if self.Sheet:
            if type(col) is int:
                try:
                    return self.Sheet.col_values(col)  # получение столбца, заданного номером
                except gspread.exceptions.IncorrectCellLabel:
                    logging.warning("Некорректный номер столбца: %s", col)
                    raise ValueError("Некорректный номер столбца: %s")
            elif type(col) is str:
                try:
                    return self.Sheet.col_values(
                        gspread.utils.a1_to_rowcol(col + "1")[1])  # получение столбца, заданного буквой
                except gspread.exceptions.APIError:
                    logging.error("Ошибка GoogleAPI, проверьте правильность имени столбца: '%s'", col)
                    raise ValueError("Ошибка GoogleAPI, проверьте правильность имени столбца: '%s'", col)
                except gspread.exceptions.IncorrectCellLabel:
                    logging.warning("Некорректное имя столбца: '%s' (Проверьте раскладку клавиатуры)", col)
                    raise ValueError("Некорректное имя столбца: '%s' (Проверьте раскладку клавиатуры)", col)
            else:
                logging.warning("Неверный формат col(столбца): %s", col)
                raise ValueError("Неверный формат col(столбца): %s", col)

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
            all_rows = self.get_column(col)
            if all_rows:
                return all_rows[row_from - 1:row_to - 1]


if __name__ == "__main__":
    # Создание(чтение) конфигурации
    config = conf.Configuration()
    # Получение конфигурационных данных о гугл-таблице
    table_config = config.get_google_table_config()
    # Открытие таблицы с помощью gspread согласно конфигурационным данным
    a = GoogleTable()
    a.set_table(table_config['URL'], table_config['Sheet'])
    # Получение списка из таблицы
    print(a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0], table_config['FIO_Rows'][1]))
    print(a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0], table_config['ID_Rows'][1]))
