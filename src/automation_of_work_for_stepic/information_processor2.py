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

connect('stepic', host='192.168.99.100', port=32770)


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

        self.courses = None
        self.students = None

    def main_1(self):
        course_id = []
        steps_id = {}

        unknown_course = []
        no_permission_course = []

        courses_id, students_id, google_names_students = self.get_config_google_data()

        student_id, unknow_user = self.create_students(students_id, google_names_students)

        # скачиваем курсы
        for c in courses_id:
            steps = self.create_course(c)

            if steps == 0:
                unknown_course.append(c)
                continue

            if steps == 1:
                no_permission_course.append(c)
                continue

            course_id.append(c)
            steps_id.update({c: steps})

        self.courses = course_id
        self.students = student_id

        # скачиваем оценки
        for s in student_id:
            for v in steps_id.values():
                self.create_grades_for_one_student(s, v)

        # считаем прогресс элементов курса
        self.create_progress()

    def create_students(self, ids, google_names):
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

    def create_course(self, course_id):
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
        for st in self.students:
            for c in self.courses:
                pr_c = 0
                count_c = 0
                date_c = []
                for s in Section.objects.filter(course=c):
                    pr_s = 0
                    count_s = 0
                    date_s = []
                    for l in Lesson.objects.filter(section=s.id):
                        pr_l = Grade.progress(student=st, steps=l.steps)
                        if pr_l == 100.0:
                            date = Grade.first_correct_date(student=st, steps=l.steps)
                            Student.add_correct_date(student=st, lesson=l.id, date=date)
                            date_s.append(date)
                        else:
                            date_s.append(None)

                        Student.add_progress(student=st, lesson=l.id, progress=pr_l)

                        pr_s += pr_l * len(l.steps)
                        count_s += len(l.steps)

                    if all(date_s):
                        date = max(date_s)
                        Student.add_correct_date(student=st, section=s.id, date=date)
                        date_c.append(date)
                    else:
                        date_c.append(None)

                    Student.add_progress(student=st, section=s.id, progress=pr_s / count_s)

                    pr_c += pr_s
                    count_c += count_s

                if all(date_c):
                    date = max(date_c)
                    Student.add_correct_date(student=st, course=c, date=date)
                else:
                    pass

                Student.add_progress(student=st, course=c, progress=pr_c / count_c)

    def get_progress_table(self):
        # создаем список курсов и студентов
        C = Course.objects.exclude('sections').filter(id__in=self.courses)
        S = Student.objects.only('id', 'name_google', 'progress_courses').filter(id__in=self.students)
        return S, C

    def get_student_page(self, student_id):

        st = Student.objects.with_id(student_id)
        co = Course.objects.filter(id__in=self.courses)

        return st, co, Section, Lesson, Step, Grade

    def get_course_page(self, course_id):
        print(Course.objects.only('title').with_id(course_id).title)
        for s in Section.objects.filter(course=course_id):
            print(s.title)
            for l in Lesson.objects.filter(section=s.id):
                print(l.title)
                for sp in l.steps:
                    # название факт прохождения корректно некорректно
                    print(Step.objects.only('position').with_id(sp).position,end='\t')
                print('')
                for st in self.students:
                    print(Student.objects.with_id(st).name_google,end='\t')
                    for s in l.steps:
                        print(Grade.objects.filter(student=st, step=sp).first().is_passed,end='\t')
                    print('')

if __name__ == "__main__":
    a = InformationsProcessor()
    # a.stepic_api.load_token()
    # a.main_1()
    a.students = [59934516, 19671119, 19618699, 19679512, 19618655, 2686236]
    a.courses = [37059]
    a.get_course_page(37059)