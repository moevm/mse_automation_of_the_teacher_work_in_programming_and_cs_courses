from automation_of_work_for_stepic.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
from automation_of_work_for_stepic.utility import singleton
import copy
from datetime import datetime, date


@singleton
class InformationsProcessor:
    def __init__(self):
        self.stepic_api = stepic_api.StepicAPI()
        self.config = conf.Configuration()  # конфигурационные данные

        self.course=None
        self.students=None

        self.incorrect = {  # некорректные данные
            'unknown_user_ids': [],
            'unknown_course_ids': [],
            'no_permission_courses': [],
            'not_enrolled_students': {}
        }

    def get_config_google_data(self):
        """
        Возвращает список список курсов из конфига и список студентов из гугл таблицы
        """
        table_config = self.config.get_google_table_config()  # получение конфигурационных данных о google-таблицы
        a = GoogleTable()
        a.set_table(table_config['URL'], table_config['Sheet'])  # получение таблицы

        google_names_students = a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0],
                                           table_config['FIO_Rows'][
                                               1])  # получение списка имен студентов из google-таблицы
        students_id = a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0],
                                 table_config['ID_Rows'][
                                     1])  # получение списка id студентов на Stepic из google-таблицы

        courses_id = self.config.get_stepic_config()['id_course']

        return courses_id,students_id,google_names_students


    def create_students(self,ids,google_names):
        """
         [
            {
                'id': student_id,
                'name_stepic': name_stepic,
                'name_google': name_google
            }
        ]
        :param ids:
        :return:
        """
        stepic_names=self.stepic_api.get_user_name(ids)
        students=[]
        incorrect=[]
        for i, gn in zip(ids, google_names):
            sn=stepic_names[ids]
            student = {'id': i, 'name_stepic': sn, 'name_google': gn}
            if sn is None:
                print(f"Неизвестный пользователь id={student['id']}")
                incorrect.append(student)
            else:
                students.append(student)
        return students,incorrect


    def create_grades(self,courses_id,students_id):
        """
        Создает список json c с оценками каждого студента каждого курса
        {
        }
        :param courses_id:
        :param students_id:
        :return:
        """
        pass

    def create_course(self, course_id):
        """
        Создаёт информацию о структуре курса название и структуру
        Если курс
            не найден возвращает 0 - первым аргументов
            если нет доступа возвращает 1 - первым аргументов
        Иначе
        Возвращает структуру курса и  id степы с задачами
        'sections': [
            {
                'id': 'section_id',
                'lessons': [
                    {
                        'id': 'lesson_id',
                        'steps': [
                                {
                                    "id": ""
                                    positions: ""
                                },
                        'title': 'lesson_title'
                    }
                ],
                "title": "section_title"
            }
        ]
        "title": "course_title"

        :param course_id:
        :return:
        """
        #скачивание курс
        course=self.stepic_api.course(course_id)
        sections=[]
        if course:
            if course['actions']:
                sections.extend(course['sections'])
                course.pop('actions')
            else:
                return 1,"no permission"
        else:
            return 0,"unknown_course_ids"

        print('sections',sections)

        #скачивание секции
        sections_info = self.stepic_api.sections(sections)
        units=[u for s in sections_info.values() for u in s['units']]
        print('units',units)

        #скачиваем юниты
        units_info = self.stepic_api.units(units)
        lessons = list(units_info.values())
        print('lesson', lessons)

        #скачиваем уроки
        lessons_info = self.stepic_api.lessons(lessons)
        steps = [u for l in lessons_info.values() for u in l['steps']]
        print('steps', steps)

        #скачиваем степа, для обозначение позиции и задачи
        steps_info=self.stepic_api.steps(steps)
        # удаляем временную информацию
        for k,v in steps_info.items():
            if 'submit' not in  v['actions']:
                steps.remove(k)
            else:
                v.pop('actions')
        print('step-issue',steps)

        #собираем
        # уроки-степы
        for l in lessons_info.values():
            l['steps'] = [steps_info[s] for s in l['steps'] if s in steps]

        #секции уроки
        for s in sections_info.values():
            s['lessons'] = [lessons_info[units_info[u]] for u in s['units']]
            s.pop('units')

        #уроки серкции
        course['sections']=[sections_info[s] for s in course['sections']]

        return course,steps


if __name__ == "__main__":
    a = InformationsProcessor()
    a.stepic_api.load_token()
    # a.load_all()
    b=a.create_course('37059')
    for i in b:
        print(i)