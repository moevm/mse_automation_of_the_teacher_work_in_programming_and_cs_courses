from google.google_table import *
from stepic_api import *
import configuration as conf

class InformationsProcessor:
    def __init__(self):
        self.stepic_api=StepicAPI()
        self.students=[]
        self.course=[]
        self.config = conf.Configuration()

    def download_users(self):
        table_config = self.config.get_google_table_config()
        'Открытие таблицы с помощью gspread согласно конфигурационным данным'
        a = GoogleTable(table_config['URL'], table_config['Sheet'])
        google_names = a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0], table_config['FIO_Rows'][1])
        ids = a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0], table_config['ID_Rows'][1])

        stepic_names = self.stepic_api.get_user_name(ids)

        return [ids, stepic_names, google_names]

    def create_jsons_user(self):
        if not self.students:
            a = self.download_users()
            list_of_st = []
            for i in range(len(a[0])):
                    student = {
                        'id': a[0][i],
                        'name_stepic': a[1][i],
                        'name_google': a[2][i],
                    }
                    list_of_st.append(student)
            self.students=list_of_st

        return self.students


    def download_course(self):
        id_course= self.config.get_stepic_config()['id_course']
        name_courses=self.stepic_api.get_course_name(id_course)
        return [id_course,name_courses]

    def create_jsons_course(self):
        if not self.course:
            a = self.download_course()
            list_of_cr = []
            for i in range(len(a[0])):
                    student = {
                        'id': a[0][i],
                        'name': a[1][i],
                    }
                    list_of_cr.append(student)
            self.course=list_of_cr
        return self.course

if __name__=="__main__":
    a=InformationsProcessor()
    print(a.download_course())