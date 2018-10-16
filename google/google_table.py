from google import google_instr as g_instr
import configuration as conf
import gspread.exceptions


class GoogleTable:

    Table = None
    Sheet = None

    def __init__(self, gc, url, sheet=0):
        """
        :param gc: gspread - GoogleAPI
        :param url: string - ссылка на таблицу
        :param sheet: int/string - номер/название листа таблицы
        """
        try:
            self.Table = gc.open_by_url(url)
        except gspread.exceptions.NoValidUrlKeyFound:
            print("Не найден корректный ключ таблицы в URL, проверьте правильность ссылки на таблицу")
        else:
            try:
                self.set_sheet(sheet)
            except gspread.exceptions.APIError:
                print("Ошибка google_api, проверьте правильность ссылки на таблицу")

    def set_sheet(self, sheet):
        """
        Сеттер текущего листа таблицы
        :param sheet: int/string - номер/название листа таблицы
        :return: -
        """
        sh = None
        if type(sheet) is int:
            sh = self.Table.get_worksheet(sheet)
        if type(sheet) is str:
            sh = self.Table.worksheet(sheet)
        if sh:
            self.Sheet = sh
        else:
            print(f"Несуществующий лист таблицы: {sheet}")

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
            return self.get_column(col)[row_from:row_to]


if __name__ == "__main__":
    'Создание(чтение) конфигурации'
    config = conf.Configuration()
    'Создание gspread для работы с таблицей'
    google_inst = g_instr.GoogleInstrument()
    'Получение конфигурационных данных о гугл-таблице'
    table_config = config.get_google_table_config()
    'Открытие таблицы с помощью gspread согласно конфигурационным данным'
    a = GoogleTable(google_inst.get_gc(), table_config['URL'], table_config['Sheet'])
    'Получение списка из таблицы'
    print(a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0], table_config['FIO_Rows'][1]))
    print(a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0], table_config['ID_Rows'][1]))
