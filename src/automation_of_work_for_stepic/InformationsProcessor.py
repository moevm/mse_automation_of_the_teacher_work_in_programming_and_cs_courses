from automation_of_work_for_stepic.google.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
import copy
import json
import os
from datetime import datetime


class InformationsProcessor:
    def __init__(self,stepic_api):
        self.stepic_api=stepic_api
        self.students=[]
        self.course=[]
        self.config = conf.Configuration()

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

    @staticmethod
    def get_course_info_from_json(course_id):
        if not os.path.exists(os.path.join('instance', course_id + '_info.json')):
            print(f"Error: load course_info: path " + "instance/" + course_id + "_info.json"+ " not found")
            return None
        with open(os.path.join('instance', course_id + '_info.json'), 'r') as f:
            info = json.load(f)
        return info

    def info_about_students(self, studs_id: list, courses_id: list):
        try:
            courses_structure = [self.get_course_info_from_json(courses_id[i]) for i in range(courses_id.__len__())]
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
                            sect_date = datetime.date(datetime.now())
                            correct_flag = False
                            for lesson in sect['lessons']:
                                steps = []
                                for step in lesson['steps']:
                                    grade = grades[i]
                                    stud_grades = grade[stud_id]
                                    passed_steps = stud_grades.__getitem__('steps')
                                    if step in passed_steps.keys():
                                        date_correct = stepic_api.StepicAPI().get_date_of_first_correct_sol_for_student(step, stud_id)
                                        if date_correct:
                                            date_correct = datetime.date(date_correct)
                                            if date_correct < sect_date:
                                                sect_date = date_correct
                                            correct_flag = True
                                        else:
                                            date_correct = '-'
                                        date_wrong = stepic_api.StepicAPI().get_date_of_first_wrong_sol_for_student(step, stud_id)
                                        if date_wrong:
                                            date_wrong = datetime.date(date_wrong)
                                        else:
                                            date_wrong = '-'
                                        steps.append(
                                            {
                                                'id': step,
                                                'is_passed': grades[i][stud_id].__getitem__('steps')[step],
                                                'first_true': 'Дата первого удачного решения: ' + str(date_correct),
                                                'first_false': 'Дата первого неудачного решения: ' + str(date_wrong),
                                            }
                                        )
                                lesson.update({'steps': steps})
                            if not correct_flag:
                                sect_date = ' - '
                            sect.update({
                                'Первое решение модуля': 'Первое решение модуля: ' + str(sect_date),
                                'Прогресс модуля': 'Прогресс модуля' + stud_id
                            })
                        course.update({'Прогресс': grades[i][stud_id]['progress']})
                    else:
                        course.update({
                            'Прогресс': 'Нет',
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

    def build_summary_table(self):
        try:
            table = []
            grades = self.course_grades()
            for stud in self.students:
                stud_courses = []
                for i in range(self.course.__len__()):
                    stud_courses.append({
                        'id': self.course[i]['id'],
                        'title': self.course[i]['title'],
                        'progress': grades[i][stud['id']]['progress']
                    })
                table.append({
                    'name': stud['name_google'],
                    'courses': stud_courses
                })
            return table
        except Exception as e:
            print(f"Error in function build_summary_table()\n\t{e}")


if __name__=="__main__":
    api = stepic_api.StepicAPI()
    api.load_token()
    a = InformationsProcessor(api)
    print(a.download_course())