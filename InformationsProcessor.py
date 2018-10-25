from google.google_table import *
from stepic_api import *
import Configuration as conf

class InformationsProcessor:

    def download_users(self):
        config = conf.Configuration()
        'Получение конфигурационных данных о гугл-таблице'
        table_config = config.get_google_table_config()
        'Открытие таблицы с помощью gspread согласно конфигурационным данным'
        a = GoogleTable(table_config['URL'], table_config['Sheet'])
        google_names = a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0], table_config['FIO_Rows'][1])
        ids = a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0], table_config['ID_Rows'][1])
        stepic_names = get_user_name(ids)
        return [ids, stepic_names, google_names]

    def create_jsons(self):
        a = self.download_users()
        list_of_st = []
        for i in range(len(a[0])):
                student = {
                    'id': a[0][i],
                    'name_stepic': a[1][i],
                    'name_google': a[2][i],
                }
                list_of_st.append(student)
        return list_of_st
