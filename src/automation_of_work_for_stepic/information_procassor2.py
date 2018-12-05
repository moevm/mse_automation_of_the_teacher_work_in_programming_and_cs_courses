from automation_of_work_for_stepic.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
from automation_of_work_for_stepic.utility import singleton
import itertools
import datetime
import copy
from datetime import datetime, date

import cProfile
def profile(func):
    """Decorator for run function profile"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.print_stats()
        return result
    return wrapper

@singleton
class InformationsProcessor:
    def __init__(self):
        self.stepic_api = stepic_api.StepicAPI()
        self.config = conf.Configuration()  # конфигурационные данные

        self.course = None
        self.students = None

        self.incorrect = {  # некорректные данные
            'unknown_user_ids': [],
            'unknown_course_ids': [],
            'no_permission_courses': [],
            'not_enrolled_students': {}
        }

    def main(self):
        S=[]
        C=[]
        G=[]

        S_id=[]
        C_id=[]
        steps_id=[]

        unknow_user=[]
        unknow_course=[]
        no_permission_course=[]


        courses_id, students_id, google_names_students=self.get_config_google_data()

        S,unknow_user=self.create_students(students_id,google_names_students)
        S_id=[s['id'] for s in S]

        #скачиваем курсы
        for c in courses_id:
            course,steps=self.create_course(c)

            if course==0:
                unknow_course.append(c)
                continue

            if course==1:
                no_permission_course.append(c)
                continue

            C.append(course)
            C_id.append(c)
            steps_id={c:steps}

        #скачиваем оценки
        for s in S_id:
            for v in steps_id.values():
                G.extend(self.create_grades_for_one_student(s,v))

        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(S_id)
        # pp.pprint(S)
        # pp.pprint(C_id)
        # pp.pprint(C)
        # pp.pprint(steps_id)
        # pp.pprint(G)


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

        students_id=[int(i) for i in students_id]
        courses_id = [int(i) for i in courses_id]

        return courses_id, students_id, google_names_students

    def create_students(self, ids, google_names):
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
        stepic_names = self.stepic_api.get_user_name(ids)
        students = []
        incorrect = []
        for i, gn in zip(ids, google_names):
            sn = stepic_names[i]
            student = {'id': i, 'name_stepic': sn, 'name_google': gn}
            if sn is None:
                print(f"Неизвестный пользователь id={student['id']}")
                incorrect.append(student)
            else:
                students.append(student)
        return students, incorrect

    def create_grades_for_one_student(self, student, steps):
        """
        Создает список json c с оценками для ОДНОГО студента!!
        {
            student=''
            step=''
            is_passed=''
            date_correct=''
            date_incorrect=''
        }
        :param courses_id:
        :param students_id:
        :return:
        """
        grades = []

        for s in steps:
            # получаем решения
            solutions, page = self.stepic_api.solutions(student, s)
            # получаем даты решений
            correct_date, wrong_date = self.get_correct_wrong_sol_date(solutions)

            data = {
                'student': student,
                'step': s,
                'is_passed': True if correct_date else False,
                'correct_date': correct_date,
                'wrong_date': wrong_date
            }

            # если есть вторая страница  и нет одной из даты
            if page and not correct_date:
                data['correct_date'] = self.stepic_api.date_first_correct_solutions(student, s)
                data['is_passed'] = True if data['correct_date'] else False

            if page and not wrong_date:
                data['wrong_date'] = self.stepic_api.date_first_wrong_solutions(student, s)

            grades.append(data)

        return grades

    def get_correct_wrong_sol_date(self, solutions):

        """
        Получает дату правильного и неправильного решений
        :param list_solutios:
        :return:
        """
        correct_date = None
        wrong_date = None
        if solutions:
            if solutions[0]['status'] == 'wrong':
                wrong_date = solutions[0]['time']

                try:
                    correct_date = next(filter(lambda x: x['status'] == 'correct', solutions))['time']
                except:
                    pass
            else:
                correct_date = solutions[0]['time']

                try:
                    wrong_date = next(filter(lambda x: x['status'] == 'wrong', solutions))['time']
                except:
                    pass
        return correct_date, wrong_date

    def create_course(self, course_id):
        """
        Создаёт информацию о структуре ОДНОГО курса название и структуру
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
        # скачивание курс
        course = self.stepic_api.course(course_id)
        sections = []
        if course:
            if course['actions']:
                sections.extend(course['sections'])
                course.pop('actions')
            else:
                return 1, "no permission"
        else:
            return 0, "unknown_course_ids"

        #print('sections', sections)

        # скачивание секции
        sections_info = self.stepic_api.sections(sections)
        units = [u for s in sections_info.values() for u in s['units']]
        #print('units', units)

        # скачиваем юниты
        units_info = self.stepic_api.units(units)
        lessons = list(units_info.values())
        #print('lesson', lessons)

        # скачиваем уроки
        lessons_info = self.stepic_api.lessons(lessons)
        steps = [u for l in lessons_info.values() for u in l['steps']]
        #print('steps', steps)

        # скачиваем степа, для обозначение позиции и задачи
        steps_info = self.stepic_api.steps(steps)
        # удаляем временную информацию
        for k, v in steps_info.items():
            if 'submit' not in v['actions']:
                steps.remove(k)
            else:
                v.pop('actions')
        #print('step-issue', steps)

        # собираем
        # уроки-степы
        for l in lessons_info.values():
            l['steps'] = [steps_info[s] for s in l['steps'] if s in steps]

        # секции уроки
        for s in sections_info.values():
            s['lessons'] = [lessons_info[units_info[u]] for u in s['units']]
            s.pop('units')

        # уроки серкции
        course['sections'] = [sections_info[s] for s in course['sections']]

        return course, steps



if __name__ == "__main__":
    a = InformationsProcessor()
    a.stepic_api.load_token()

    a.main()
