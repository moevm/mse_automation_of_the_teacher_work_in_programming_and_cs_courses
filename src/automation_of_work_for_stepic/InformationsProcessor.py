from automation_of_work_for_stepic.google.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
import copy
import json
import os
from datetime import datetime, date


class InformationsProcessor:
    def __init__(self):
        self.stepic_api = stepic_api.StepicAPI()
        self.students = []
        self.course = []
        self.config = conf.Configuration()
        self.courses_structure = []

    def download_users(self):
        table_config = self.config.get_google_table_config()
        #'Открытие таблицы с помощью gspread согласно конфигурационным данным'
        a = GoogleTable()
        a.set_table(table_config['URL'], table_config['Sheet'])

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
        """
        Возвращает массив с перечислением id и имен курсов.
        :return: двумерный массив с id и соответствующими именами курсов
        """
        id_course = self.config.get_stepic_config()['id_course']
        name_courses =self.stepic_api.get_course_name(id_course)
        return [[str(i) for i in id_course], name_courses]

    def create_jsons_course(self):
        """
        Создает json курсов при его отсутствии с перечислением id и имен курсов.
        :return: json курсов
        """
        if not self.course:
            a = self.download_course()
            list_of_cr = []
            for i in range(len(a[0])):
                    course = {
                        'id': a[0][i],
                        'title': a[1][i],
                    }
                    list_of_cr.append(course)
            self.course = list_of_cr
        return self.course

    def course_grades(self):
        """
        По данным из json со статистикой курсов и данным по id студентов возвращает статистику прохождения
        курса по каждому студенту в %. При отстутствии студента на курсе возвращает "нет"
        :return: возвращает массив с %-ми прохождения курсов по каждому студенту
        """
        if self.students and self.course:
            result = []
            grades = [self.stepic_api.get_course_statistic(c['id']) for c in self.course]
            id_users = [st['id'] for st in self.students]

            for gr in grades:
                res_dict = {}
                for user in id_users:
                    res = [self.calculate_progress(i) for i in gr if str(i['user']) == user]
                    if res:
                        res_dict.update(res[0])
                    else:
                        res_dict.update({
                            user: {
                                'progress': 'Нет',
                                'steps': {}
                            }
                        })
                result.append(res_dict)
            return result

    def calculate_progress(self,grade_user):
        """
        Принимает на вход статистику студента по прохождению курса, где для каждого модуля указано, пройден он или нет.
        Возвращает процент прохождения студентом курса.
        :param grade_user: json статистики студента по прохождению курса
        :return: строка с % прохождения студентом курса
        """
        result = grade_user['results']
        progress = 0
        flag_steps = {}
        for v in result.values():
            flag_steps[str(v['step_id'])] = v['is_passed']
            if v['is_passed']:
                progress+=1
        return {
            str(grade_user['user']):
                {
                    'progress': str(progress / len(result) * 100) + '%',
                    'steps': flag_steps
                }
        }

    def create_course_structures(self):
        """
        Сохраняет структуры курсов в поле InformationsProcessor
        :return:
        """
        try:
            self.courses_structure = [self.stepic_api.get_course_info(i['id']) for i in self.course]
        except Exception as e:
            print(f"Error in function create_course_structures\n\t{e}")
            raise e

    def info_about_students(self, studs_id: list, courses_id: list):
        """
        Возвращает информацию о прохождении студентами курсов
        :param studs_id: [str] - список id студентов
        :param courses_id: [str] - список id курсов
        :return: [{}] - список информаций по каждому студенту
        """
        try:
            courses_structure = [self.stepic_api.get_course_info(courses_id[i]) for i in range(courses_id.__len__())]
            studs_info = []
            for stud_id in studs_id:
                stud = None
                for i in self.students:
                    if i['id'] == stud_id:
                        stud = i
                        break
                stud_courses = []
                grades = self.course_grades()
                for i in range(courses_id.__len__()):
                    course = copy.deepcopy(courses_structure[i])
                    if grades[i][stud_id]['steps']:
                        for sect in course['sections']:
                            sect_date = date(1970, 1, 1)
                            step_counter = 0
                            correct_step_counter = 0
                            for lesson in sect['lessons']:
                                steps = []
                                for step in lesson['steps']:
                                    grade = grades[i]
                                    stud_grades = grade[stud_id]
                                    passed_steps = stud_grades.__getitem__('steps')
                                    if step in passed_steps.keys():
                                        step_counter += 1
                                        date_correct = stepic_api.StepicAPI().get_date_of_first_correct_sol_for_student(step, stud_id)
                                        if date_correct:
                                            correct_step_counter += 1
                                            date_correct = datetime.date(date_correct)
                                            if date_correct > sect_date:
                                                sect_date = date_correct
                                            date_correct = date_correct.strftime("%d.%m.%Y")
                                        else:
                                            date_correct = '-'
                                        date_wrong = stepic_api.StepicAPI().get_date_of_first_wrong_sol_for_student(step, stud_id)
                                        if date_wrong:
                                            date_wrong = datetime.date(date_wrong).strftime("%d.%m.%Y")
                                        else:
                                            date_wrong = '-'
                                        steps.append(
                                            {
                                                'id': step,
                                                'is_passed': grades[i][stud_id].__getitem__('steps')[step],
                                                'first_true': date_correct,
                                                'first_false': date_wrong,
                                            }
                                        )
                                lesson.update({'steps': steps})
                            if correct_step_counter != step_counter:
                                sect_date = '-'
                            else:
                                sect_date = sect_date.strftime("%d.%m.%Y")
                            sect.update({
                                'date': sect_date,
                                'progress': str(100*correct_step_counter/step_counter) + '%',
                                'is_passed': correct_step_counter == step_counter
                            })
                        course.update({'progress': grades[i][stud_id]['progress']})
                    else:
                        course.update({
                            'progress': 'Нет',
                            'sections': []
                            })
                    stud_courses.append(course)
                studs_info.append({
                    'id': stud_id,
                    'name_stepic': stud['name_stepic'],
                    'name_google': stud['name_google'],
                    'courses': stud_courses
                })
            return studs_info
        except Exception as e:
            print(f"Error in function info_about_students (studs_id={studs_id}, courses_id={courses_id})\n\t{e}")
            raise e

    def create_table_step_info(self, course_id):
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
            for stud in self.students:
                course = [i for i in self.courses_structure if i['id'] == course_id][0]
                student_table_rows = [self.step_info(step, stud['id']) for sect in course['sections'] for lesson in sect['lessons'] for step in lesson['steps']]
                for row in student_table_rows:
                    row.insert(1, stud['name_stepic'])
                # table.append(student_table_rows) # с внутренней группировкой по студентам [[строки студента1], [строки студента2], [строки студента3]]
                table += student_table_rows # без внутренней группировки [строки студента1, строки студента2, строки студента3]
            return table
        except Exception as e:
            print(f"Error in function create_table_step_info (courses_id={course_id})\n\t{e}")
            raise e

    def step_info(self, step_id, stud_id):
        """
        Возвращает информацию о прохождении студентом шага = [stud_id, id_step, date_first_solve, is_solved]
        :param step_id: str - id степа
        :param stud_id: str - id студента
        :return: []
        """
        date_correct = self.stepic_api.get_date_of_first_correct_sol_for_student(step_id, stud_id)
        correct_flag = True
        if date_correct:
            date_correct = datetime.date(date_correct).strftime("%d.%m.%Y")
        else:
            date_correct = '-'
            correct_flag = False
        return [
            stud_id,
            step_id,
            date_correct,
            correct_flag
        ]


if __name__ == "__main__":
    a = InformationsProcessor()
    a.stepic_api.load_token()
    a.create_jsons_course()
    a.create_jsons_user()
    a.create_course_structures()
    courses = [i['id'] for i in a.course]
    students = [i['id'] for i in a.students]
    print(a.create_table_step_info(courses[0]))
