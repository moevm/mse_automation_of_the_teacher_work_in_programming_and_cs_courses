import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleInstrument:
    _GC = 0

    def __init__(self):
        self.init_gc()

    def init_gc(self):
        """
        Инициализация gspread для работы с GoogleAPI
        :return: -
        """
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'resources/private key for GoogleAPI.json', scope)
        self._GC = gspread.authorize(credentials)

    def get_gc(self):
        """
        Геттер gspread
        :return: поле _GC - gspread
        """
        return self._GC
