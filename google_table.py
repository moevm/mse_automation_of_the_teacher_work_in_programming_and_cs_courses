import google_instr as g_instr
import configuration as conf


class GoogleTable:

    Table = 0
    Sheet = 0

    def __init__(self, gc, url, sheet=0):
        """
        :param gc: gspread - GoogleAPI
        :param url: string - ссылка на таблицу
        :param sheet: int/string - нормер/название листа таблицы
        """
        self.Table = gc.open_by_url(url)
        self.set_sheet(sheet)

    def set_sheet(self, sheet):
        """
        Сеттер текущего листа таблицы
        :param sheet: int/string - номер/название листа таблицы
        :return: -
        """
        self.Sheet = self.Table.get_worksheet(sheet)

    def get_column(self, num):
        """
        Геттер столбца
        :param num: int - номер требуемого столбца
        :return: [] - список значений всех ячеек столбца
        """
        return self.Sheet.col_values(num)

    def get_row(self, num):
        """
        Геттер строки
        :param num: int - номер требуемой строки
        :return: [] - список значений всех ячеек строки
        """
        return self.Sheet.row_values(num)

    def get_list(self, col, row_from, row_to):
        """
        Геттер списка строк столбца из заданного диапазона
        :param col: int - номер столбца
        :param row_from: int -начало диапазона строк
        :param row_to: int -конец диапазона строк
        :return: [] - список значений ячеек требуемого диапазона строк из столбца
        """
        return self.get_column(col)[row_from:row_to]


if __name__ == "__main__":
    'Создание(чтение) конфигурации'
    config = conf.Configuration()
    'Создание gspread для работы с таблицей'
    google_inst = g_instr.GoogleInstrument()
    'Открытие таблицы с помощью gspread согласно конфигурационным данным'
    a = GoogleTable(google_inst.get_gc(), config.get_config_by_key('URL'), config.get_config_by_key('Sheet'))
    'Получение списка из таблицы'
    print(a.get_list(config.get_config_by_key('Col'), config.get_config_by_key('Rows')[0], config.get_config_by_key('Rows')[1]))
