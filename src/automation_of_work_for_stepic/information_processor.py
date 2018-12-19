from automation_of_work_for_stepic.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
from automation_of_work_for_stepic.utility import singleton
import copy
from datetime import datetime, date


@singleton
class InformationsProcessor:
    def __init__(self):
        self.stepic_api = stepic_api.StepicAPI()  # для работы со StepicApi
        self.students = []  # информация о студентах [{'id': student_id, 'name_stepic': name_stepic, 'name_google': name_google}]
        self.courses = []  # информация о курсах
        self.config = conf.Configuration()  # конфигурационные данные
        self.course_grades = []  # статистика курсов
        self.incorrect = {  # некорректные данные
            'unknown_user_ids': [],
            'unknown_course_ids': [],
            'no_permission_courses': [],
            'not_enrolled_students': {}
        }

    def load_all(self):
        self.create_courses()  # загрузка информации о курсе
        self.create_students()  # загрузка информации о студентах
        self.create_course_grades()  # загрузка информации о статистике прохождения курсов
        self.add_course_structures()  # создание структуры курсов
        self.add_info_about_students()  # создание полной информации о прохождении курсов студентами

    def download_students(self):
        """
        Получение id и имён студентов из google-таблицы и определение их имени на Stepic
        Возвращает таблицу вида:
        [
            [id1, id2],
            [stepic_name1, stepic_name2],
            [google_name1, google_name2],
        ]
        :return: [[]]
        """
        table_config = self.config.get_google_table_config()  # получение конфигурационных данных о google-таблицы
        a = GoogleTable()
        a.set_table(table_config['URL'], table_config['Sheet'])  # получение таблицы

        google_names = a.get_list(table_config['FIO_Col'], table_config['FIO_Rows'][0],
                                  table_config['FIO_Rows'][1])  # получение списка имен студентов из google-таблицы
        ids = a.get_list(table_config['ID_Col'], table_config['ID_Rows'][0],
                         table_config['ID_Rows'][1])  # получение списка id студентов на Stepic из google-таблицы

        stepic_names = self.stepic_api.get_user_name(ids)  # получение списка имён студентов на Stepic по их id
        return [ids, stepic_names, google_names]

    def create_students(self):
        """
        Возвращает информацию о студентах
        self.students = [
            {
                'id': student_id,
                'name_stepic': name_stepic,
                'name_google': name_google
            }
        ]
        :return: self.students
        """
        if not self.students:
            info = self.download_students()  # получение информации о студентах
            self.students = [{'id': stud_id, 'name_stepic': info[1][i], 'name_google': info[2][i]} for i, stud_id in
                             enumerate(info[0])]  # формирование данных о студентах
            for student in self.students:
                if not student['name_stepic']:
                    print(f"Неизвестный пользователь id={student['id']}")
                    self.incorrect['unknown_user_ids'].append(student)
                    self.students.remove(student)
        return self.students

    def create_courses(self):
        """
        Возвращает информацию о курсах
        self.courses = [
            {
                'id': course_id,
                'title': course_title
            }
        ]
        """
        if not self.courses:
            try:
                self.courses = [{'id': str(i), 'title': self.stepic_api.get_course_name(str(i))} for i in
                                self.config.get_stepic_config()['id_course']]  # формирование данных о курсах
                for course in self.courses:
                    if not course['title']:
                        print(f"Неизвестный курс id={course['id']}")
                        self.incorrect['unknown_course_ids'].append(course)
                        self.courses.remove(course)
            except Exception as e:
                print(f"Error in function courses_info\n\t{e}")
                raise e
        return self.courses

    def create_course_grades(self):
        """
        По данным из json со статистикой курсов и данным по id студентов заполняет поле self.course_grades - статистику прохождения
        курса по каждому студенту в %. При отстутствии студента на курсе возвращает "нет"
        [
            {
                'student_id':
                {
                    'progress': 'xx.x%' (or 'Нет'),
                    'steps':
                    {
                        'step_id': is_passed
                    }
                }
            }
        ]
        :return: self.course_grades
        """
        if not self.course_grades:
            if self.students and self.courses:
                result = []
                grades = [self.stepic_api.get_course_statistic(c['id']) for c in
                          self.courses]  # получение статистики по курсу
                student_ids = [st['id'] for st in self.students]  # список id всех студентов
                for i, gr in enumerate(grades):
                    if gr:
                        res_dict = {}
                        for student in student_ids:
                            res = [self.calculate_progress(i) for i in gr if
                                   str(i['user']) == student]  # подсчет прогресса студента
                            # сохранение прогресса студента по курсу
                            if res:
                                res_dict.update(res[0])  # прогресс существует
                            else:
                                if str(gr[0]['course']) not in self.incorrect['not_enrolled_students']:
                                    self.incorrect['not_enrolled_students'].update({str(gr[0]['course']): []})
                                self.incorrect['not_enrolled_students'][str(gr[0]['course'])].append(student)
                                res_dict.update({  # прогресс отсутсвует (=студент не поступил на курс)
                                    student: {
                                        'progress': 'Нет',
                                        'steps': {}
                                    }
                                })
                        result.append(res_dict)  # сохранение прогресса студентов по курсу
                    else:
                        print(f"Нет доступа к курсу {self.courses[i]}")
                        self.incorrect['no_permission_courses'].append(self.courses[i])
                        self.courses.remove(self.courses[i])
                self.course_grades = result
        return self.course_grades

    def calculate_progress(self, grade_user):
        """
        Принимает на вход статистику студента по прохождению курса, где для каждого шага указано, пройден он или нет.
        Возвращает процент прохождения курса и факт прохождения студентом каждого шага
        {
            stud_id:
                {
                    'progress': 'xx.x%',
                    'steps':
                    {
                        step_id: is_passed
                    }
                }
        }
        :param grade_user: статистика студента по прохождению курса
        :return: {} с данными о %-ом прохождении курса и о факте прохождения всех шагов курса
        """
        result = grade_user['results']
        progress = 0
        flag_steps = {}
        for v in result.values():
            flag_steps[str(v['step_id'])] = v['is_passed']  # сохранение факта прохождения шага
            if v['is_passed']:
                progress += 1  # подсчёт кол-ва решенных шагов
        return {
            str(grade_user['user']):
                {
                    'progress': str(progress / len(result) * 100) + '%',  # подсчет % прохождения курса студентом
                    'steps': flag_steps  # флаги прохождения шагов
                }
        }

    def add_info_about_students(self):
        """
        Создаёт информацию о прохождении студентами курсов, дополняя элементы self.students полем
        'courses':[
            {
                'id': course_id,
                'progress': 'xx.x%',
                'sections': [
                    {
                        'date': 'dd.mm.yyyy'(or '-'),
                        'id': section_id,
                        'is_passed': True/False,
                        'lessons': [
                            {
                                'id': lesson_id,
                                'steps': [
                                    {
                                        'first_false': 'dd.mm.yyyy'(or '-'),
                                        'first_true': 'dd.mm.yyyy'(or '-'),
                                        'id': step_id,
                                        'is_passed': True/False
                                    }
                                ],
                                'title': lesson_title
                            }
                        ],
                        'progress': 'xx.x%',
                        'title': section_title
                    }
                ],
                'title': course_title
            }
        ]
        """
        try:
            for student in self.students:  # для каждого студента
                stud_courses = []
                for i, course in enumerate(self.courses):  # для каждого курса
                    course = copy.deepcopy(course)  # глубокое копирование структуры курса
                    if self.course_grades[i][student['id']][
                        'steps']:  # если статистика прохождения студента не пуста (он поступил на курс)
                        for sect in course['sections']:  # для всех модулей курса
                            sect_date = date(1970, 1,
                                             1)  # для определения последнего решения модуля, в случае его полного прохождения
                            step_counter = 0  # счетчик кол-ва всех шагов
                            correct_step_counter = 0  # счетчик кол-ва верно решенных шагов
                            for lesson in sect['lessons']:  # для всех уроков модуля
                                steps = []
                                for step in lesson['steps']:  # для всех шагов урока
                                    if step in self.course_grades[i][student['id']][
                                        'steps']:  # если шаг существует в статистике(шаг с решением)
                                        step_counter += 1  # увеличение счетчика шагов
                                        date_correct = self.stepic_api.get_date_of_first_correct_sol_for_student(step,
                                                                                                                 student[
                                                                                                                     'id'])  # получение даты первого верного решения
                                        if date_correct:
                                            correct_step_counter += 1  # если дата существует - шаг пройден - увеличение счетчига верно решенных шагов
                                            date_correct = datetime.date(date_correct)
                                            if date_correct > sect_date:  # определение самого позднего решения в модуле
                                                sect_date = date_correct
                                            date_correct = date_correct.strftime("%d.%m.%Y")
                                        else:
                                            date_correct = '-'  # верное решение отсутсвует - шаг не пройден
                                        date_wrong = self.stepic_api.get_date_of_first_wrong_sol_for_student(step,
                                                                                                             student[
                                                                                                                 'id'])  # получение даты первого неверного решения
                                        if date_wrong:
                                            date_wrong = datetime.date(date_wrong).strftime("%d.%m.%Y")
                                        else:
                                            date_wrong = '-'  # неверное решение отсутсвует
                                        steps.append(  # сохранение информации о шаге
                                            {
                                                'id': step,
                                                'is_passed': self.course_grades[i][student['id']]['steps'][step],
                                                'first_true': date_correct,
                                                'first_false': date_wrong,
                                            }
                                        )
                                lesson.update({'steps': steps})  # сохранение информцаии о шагах в уроке
                            if correct_step_counter != step_counter:
                                sect_date = '-'  # модуль не пройден полностью - дата последнего верного решения модуля отсутствует
                            else:
                                sect_date = sect_date.strftime(
                                    "%d.%m.%Y")  # последнее верное решение в модуле, если он пройден полностью
                            sect.update({
                                'date': sect_date,
                                'progress': str(100 * correct_step_counter / step_counter) + '%',
                                'is_passed': correct_step_counter == step_counter
                            })  # сохранение информцаии об уроках в модуле
                        course.update({'progress': self.course_grades[i][student['id']][
                            'progress']})  # сохранение информцаии о модулях в курсе, если прогресс существует (студент поступил на курс)
                    else:
                        course.update({
                            'progress': 'Нет',
                            'sections': []
                        })  # студент не поступил на курс - статистика о прохождении отсутствует
                    stud_courses.append(course)  # сохранение информации о курсе для студента
                student.update({'courses': stud_courses})  # информация о курсах студента
        except Exception as e:
            print(f"Error in function add_info_about_students\n\t{e}")
            raise e

    def add_course_structures(self):
        """
        Создаёт информацию о структуре курса, дополняя элементы self.courses полем
        'sections': [
            {
                'id': 'section_id',
                'lessons': [
                    {
                        'id': 'lesson_id',
                        'steps': ['step_id'],
                        'title': 'lesson_title'
                    }
                ],
                "title": "section_title"
            }
        ]
        """
        try:
            for course in self.courses:  # для каждого курса
                course['sections'] = self.stepic_api.course_structure(course['id'])  # получение структуры курса
        except Exception as e:
            print(f"Error in function add_course_structures\n\t{e}")
            raise e

    def table_step_info(self, course_id):
        """
        Возвращает таблицу вида
        [
            [id_stud, name_stud, id_step, date_first_solve, is_solved]
        ]
        с информацией о прохождении степов курса студентами
        :param course_id: str - id курса
        :return: [[]]
        """
        try:
            table = []
            for student in self.students:
                course = [i for i in self.courses if i['id'] == course_id][0]
                student_table_rows = [self.short_step_info(step, student['id']) for sect in course['sections'] for
                                      lesson in sect['lessons'] for step in lesson['steps']]
                for row in student_table_rows:
                    row.insert(1, student['name_stepic'])
                # table.append(student_table_rows) # с внутренней группировкой по студентам [[строки студента1], [строки студента2], [строки студента3]]
                table += student_table_rows  # без внутренней группировки [строки студента1, строки студента2, строки студента3]
            return table
        except Exception as e:
            print(f"Error in function table_step_info (courses_id={course_id})\n\t{e}")
            raise e

    def short_step_info(self, step_id, stud_id):
        """
        Возвращает краткую информацию о прохождении студентом шага = [stud_id, id_step, date_first_solve, is_solved]
        :param step_id: str - id степа
        :param stud_id: str - id студента
        :return: []
        """
        date_correct = self.stepic_api.get_date_of_first_correct_sol_for_student(step_id, stud_id)
        is_passed = True
        if date_correct:
            date_correct = datetime.date(date_correct).strftime("%d.%m.%Y")
        else:
            date_correct = '-'
            is_passed = False
        return [
            stud_id,
            step_id,
            date_correct,
            is_passed,
        ]

    def get_student_by_id(self, stud_id: str):
        try:
            student = [stud for stud in self.students if stud_id == stud['id']]
            if student:
                return student[0]
            else:
                print(f"Неизветсный студент id={stud_id}")
        except Exception as e:
            print(f"Error in function get_student_info (stud_id={stud_id})\n\t{e}")
            raise e

    def get_course_by_id(self, course_id: str):
        try:
            course = [course for course in self.courses if course_id == course['id']]
            if course:
                return course[0]
            else:
                print(f"Неинициализированный курс id={course_id}")
        except Exception as e:
            print(f"Error in function get_course_by_id (course_id={course_id})\n\t{e}")
            raise e


if __name__ == "__main__":
    a = InformationsProcessor()
    a.stepic_api.load_token()
    a.load_all()
    print(a.table_step_info(a.courses[0]['id']))
