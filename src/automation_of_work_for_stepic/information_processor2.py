from automation_of_work_for_stepic.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
from automation_of_work_for_stepic.utility import singleton
from automation_of_work_for_stepic.mongo_model import *
from mongoengine import connect
import itertools
import datetime
import copy
from datetime import datetime, date

import cProfile

connect('stepic', host='192.168.99.100', port=32768)


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
        S = []
        C = []
        G = []

        S_id = []
        C_id = []
        steps_id = []

        unknow_user = []
        unknow_course = []
        no_permission_course = []

        courses_id, students_id, google_names_students = self.get_config_google_data()

        S, unknow_user = self.create_students(students_id, google_names_students)
        S_id = [s['id'] for s in S]

        # скачиваем курсы
        for c in courses_id:
            course, steps = self.create_course(c)

            if course == 0:
                unknow_course.append(c)
                continue

            if course == 1:
                no_permission_course.append(c)
                continue

            C.append(course)
            C_id.append(c)
            steps_id.update({c: steps})

        # скачиваем оценки
        for s in S_id:
            for v in steps_id.values():
                G.extend(self.create_grades_for_one_student(s, v))

        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(S_id)
        pp.pprint(S)
        pp.pprint(C_id)
        pp.pprint(C)
        pp.pprint(steps_id)
        pp.pprint(G)

    def main_1(self):
        S_id = []
        C_id = []
        steps_id = {}

        unknow_course = []
        no_permission_course = []

        courses_id, students_id, google_names_students = self.get_config_google_data()

        S_id, unknow_user = self.create_students_1(students_id, google_names_students)

        # скачиваем курсы
        for c in courses_id:
            steps = self.create_course_1(c)

            if steps == 0:
                unknow_course.append(c)
                continue

            if steps == 1:
                no_permission_course.append(c)
                continue

            C_id.append(c)
            steps_id.update({c: steps})

        # скачиваем оценки
        for s in S_id:
            for v in steps_id.values():
                self.create_grades_for_one_student_1(s, v)

        # считаем прогресс элементов курса
        self.create_progress()

        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(unknow_user)
        # pp.pprint(unknow_course)
        # pp.pprint(no_permission_course)
        #
        # pp.pprint(S_id)
        # pp.pprint(C_id)
        # pp.pprint(steps_id)

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

        students_id = [int(i) for i in students_id]
        courses_id = [int(i) for i in courses_id]

        return courses_id, students_id, google_names_students

    def create_students(self, ids, google_names):
        """
         [
            {
                'id': student_id,
                'name_stepic': name_stepic,
                'name_stepic': name_google
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
            ##
            if sn is None:
                print(f"Неизвестный пользователь id={student['id']}")
                incorrect.append(gn + '(' + str(i) + ')')
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
            # вставка в бд
            Grade(**data).save()

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

        # print('sections', sections)

        # скачивание секции
        sections_info = self.stepic_api.sections(sections)
        units = [u for s in sections_info.values() for u in s['units']]
        # print('units', units)

        # скачиваем юниты
        units_info = self.stepic_api.units(units)
        lessons = [u['lesson'] for u in units_info.values()]
        # print('lesson', lessons)

        # скачиваем уроки
        lessons_info = self.stepic_api.lessons(lessons)
        steps = [u for l in lessons_info.values() for u in l['steps']]
        # print('steps', steps)

        # скачиваем степы, для обозначение позиции и задачи
        steps_info = self.stepic_api.steps(steps)
        # удаляем временную информацию
        for k, v in steps_info.items():
            if 'submit' not in v['actions']:
                steps.remove(k)
            else:
                v.pop('actions')
        # print('step-issue', steps)

        # собираем
        # уроки-степы
        for i, l in lessons_info.items():
            l['steps'] = [steps_info[s] for s in l['steps'] if s in steps]
            # await на скачку степов
            # по всем студентам
            # for st in self.students:
            #    # загружаем в бд все степы урока
            #    self.create_grades_for_one_student(st, l['steps'])
            #    # считает прогресс
            #    pr = Grade.progress(st, l['steps'])
            #    # записываем в базу данных
            #    Student.add_progress(st, student=st, lessons=i,progress=pr)

        # секции уроки
        for s in sections_info.values():
            s['lessons'] = [units_info[u]['lesson'] for u in s['units']]
            s.pop('units')

        # уроки серкции
        course['sections'] = [sections_info[s] for s in course['sections']]

        return course, steps

    def create_students_1(self, ids, google_names):
        """
         [
            {
                'id': student_id,
                'name_stepic': name_stepic,
                'name_stepic': name_google
            }
        ]
        :param ids:
        :return:
        """
        stepic_names = self.stepic_api.get_user_name(ids)
        incorrect = []
        students_id = []
        for i, gn in zip(ids, google_names):
            sn = stepic_names[i]
            if sn is None:
                print(f"Неизвестный пользователь id={i}")
                incorrect.append(gn + '(' + str(i) + ')')
            else:
                Student(id=i, name_stepic=sn, name_google=gn).save()
                students_id.append(i)

        return students_id, incorrect

    def create_grades_for_one_student_1(self, student, steps):
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

            Grade(**data).save()

    def create_course_1(self, course_id):
        course = self.stepic_api.course(course_id, attribute=['id', 'title', 'sections', 'actions'])
        if course:
            if course['actions']:
                course.pop('actions')
            else:
                return 1
        else:
            return 0

        steps = self.create_sections(course['sections'])
        Course(**course).save()
        return steps

    def create_sections(self, sections_id):
        sections = self.stepic_api.sections(sections_id, attribute=['id', 'title', 'units', 'course'])
        units_id = [u for s in sections.values() for u in s['units']]
        units, steps = self.create_units_lessons(units_id)

        for s in sections.values():
            s['lessons'] = [units[u]['lesson'] for u in s['units']]
            s.pop('units')
            Section(**s).save()
        return steps

    def create_units_lessons(self, units_id):
        units = self.stepic_api.units(units_id, attribute=['lesson', 'section'])
        lessons_id = [u['lesson'] for u in units.values()]
        lessons = self.stepic_api.lessons(lessons_id, attribute=['id', 'title', 'steps'])
        steps_id = []
        for u in units.values():
            steps_id.extend(lessons[u['lesson']]['steps'])

            Lesson(section=u['section'], **(lessons[u['lesson']])).save()

        self.create_steps(steps_id)
        return units, steps_id

    def create_steps(self, steps_id):
        steps = self.stepic_api.steps(steps_id, attribute=['id', 'position', 'actions', 'lesson'])
        # удаляем временную информацию
        for k, v in steps.items():
            if 'submit' not in v['actions']:
                Lesson.objects.with_id(v['lesson']).update(pull__steps=k)
            else:
                v.pop('actions')
                # добавляем в базу
                Step(**v).save()

    def create_progress(self):
        student_id = [59934516, 19671119, 19618699, 19679512, 19618655, 2686236]
        course_id = [37059]
        for st in student_id:
            for c in course_id:
                pr_c = 0
                count_c = 0
                for s in Section.objects.filter(course=c):
                    pr_s = 0
                    count_s = 0
                    for l in Lesson.objects.filter(section=s.id):
                        pr_l = Grade.progress(student=st, steps=l.steps)
                        Student.add_progress(student=st, lesson=l.id, progress=pr_l)

                        pr_s += pr_l * len(l.steps)
                        count_s += len(l.steps)

                    Student.add_progress(student=st, section=s.id, progress=pr_s / count_s)

                    pr_c += pr_s
                    count_c += count_s

                Student.add_progress(student=st, course=c, progress=pr_c / count_c)

    def get_progress_table(self):
        student_id = [59934516, 19671119, 19618699, 19679512, 19618655, 2686236]
        course_id = [37059]
        grade = {37059: [473226, 467153, 473228, 467156, 467155, 467157, 467149, 473231]}

        # создаем список курсов

        C = [Course.objects.exclude('sections').with_id(c) for c in course_id]
        S = [Student.objects.only('id', 'name_google', 'progress_courses').with_id(s) for s in student_id]

        print(C)
        print(S)
        return S,C

    def get_student_page(self, student_id):
        course_id = [37059]

        st = Student.objects.with_id(student_id)
        co = Course.objects.filter(id__in=course_id)

        # print(st.name_google)
        # print(st.name_stepic)
        #
        # for c in co:
        #     print(c.title)
        #     print(st.progress_courses[str(c.id)])
        #     for s in Section.objects.filter(course=c.id):
        #         print('\t',s.title)
        #         print('\t',st.progress_sections[str(s.id)])
        #         for l in Lesson.objects.filter(section=s.id):
        #             print('\t','\t',l.title)
        #             print('\t','\t',st.progress_lessons[str(l.id)])
        #             for sp in l.steps:
        #                 print(Step.objects.with_id(sp).position)
        #                 g = Grade.objects.filter(student=st.id, step=sp).first()
        #                 print('\t','\t','\t',g.is_passed)
        #                 print('\t','\t','\t',g.wrong_date)
        #                 print('\t','\t','\t',g.correct_date)
        return st,co,Section,Lesson,Step,Grade

    def get_course_page(self, course_id):
        student_id = [59934516, 19671119, 19618699, 19679512, 19618655, 2686236]
        Course.objects.only('title').with_id(course_id).title
        for s in Section.objects.filter(course=course_id):
            s.title
            for l in Lesson.objects.filter(section=s):
                l.title
                for st in student_id:
                    for s in l.steps:
                        # название факт прохождения корректно некорректно
                        Step.objects.only('position').with_id(s).position
                        g = Grade.objects.filter(student=st, step=s).first()
                        g.is_passed


if __name__ == "__main__":
    a = InformationsProcessor()
    a.stepic_api.load_token()
    # a.stepic_api.load_token()
    #a.main_1()
    a.main_1()
