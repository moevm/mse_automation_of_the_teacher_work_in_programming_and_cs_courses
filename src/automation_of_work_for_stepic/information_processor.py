from automation_of_work_for_stepic.google_table import GoogleTable
from automation_of_work_for_stepic import configuration as conf
from automation_of_work_for_stepic import stepic_api
from automation_of_work_for_stepic.utility import singleton
from automation_of_work_for_stepic.mongo_model import *
from mongoengine.connection import get_db

from datetime import datetime

@singleton
class InformationsProcessor:
    def __init__(self,user_id=None):
        """
        """
        self.stepic_api = stepic_api.StepicAPI()
        self.config = None  # конфигурационные данные
        self.incorrect = None
        self.students = []
        self.courses = []
        self.user = None
        self.loaded = False

        if user_id:
            if self.user_loaded(user_id):
                self.load_exist(user_id)
                self.loaded=True
            else:
                self.create_user(user_id)
                self.loaded = False

    def load_new(self):
        """
        Скачивает информацию со степика
        :return:
        """
        db = get_db()
        for coll in db.list_collection_names():
            db.drop_collection(coll)

        self.user.save()

        course_id = []
        steps_id = {}

        unknown_course = []
        no_permission_course = []

        self.create_config()

        #получаем инфу со степика
        courses_id, students_id, google_names_students = self.get_google_table_info()

        #скачиваем инфу о студентах
        student_id, unknown_student = self.create_students(students_id, google_names_students)

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

        self.config.students=self.students
        self.config.courses=self.courses
        self.config.save()
        # скачиваем оценки
        for s in student_id:
            for v in steps_id.values():
                self.create_grades_for_one_student(s, v)

        # считаем прогресс элементов курса
        self.create_progress()

        #загружаем в бд некорректные значения
        self.create_incorrect(unknown_student,unknown_course,no_permission_course)
        self.user.last_update=datetime.now()
        self.user.save()
        self.loaded=True

    def load_exist(self,user_id):
        """
        Загружаем уже загруженные данные
        :param user_id:
        :return:
        """
        self.user=User.objects.with_id(user_id)
        self.config=Config.objects.with_id(user_id)
        self.incorrect=Incorrect.objects.with_id(user_id)
        self.students=self.config.students
        self.courses=self.config.courses
        self.loaded=True

    def get_google_table_info(self):
        table_config = self.config.google_table  # получение конфигурационных данных о google-таблицы
        a = GoogleTable()

        a.set_table(table_config.URL, table_config.Sheet)  # получение таблицы

        google_names_students = a.get_list(table_config.FIO_Col, table_config.FIO_Rows[0],
                                           table_config.FIO_Rows[
                                               1])  # получение списка имен студентов из google-таблицы
        students_id = a.get_list(table_config.ID_Col, table_config.ID_Rows[0],
                                 table_config.ID_Rows[1])  # получение списка id студентов на Stepic из google-таблицы

        courses_id = self.config.stepic.id_course
        students_id = [int(i) for i in students_id]
        courses_id = [int(i) for i in courses_id]

        return courses_id, students_id, google_names_students

    def user_loaded(self,user_id):
        return User.objects.with_id(user_id) and User.objects.with_id(user_id).last_update

    ## создание таблиц

    def create_user(self, user_id):
        self.user = User(user_id)
        self.user.save()


    def create_config(self):
        """
        Возвращает список список курсов из конфига и список студентов из гугл таблицы
        """
        conf.Configuration().load_config()

        self.config = Config(id=self.user.id,**(conf.Configuration().get_data()))
        self.config.save()

    def create_incorrect(self,unknown_student,unknown_course,no_permission_course):
        self.incorrect=Incorrect(id=self.user.id, unknown_student=unknown_student, unknown_course=unknown_course, no_permission_course=no_permission_course)
        self.incorrect.save()

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
        Скачивает решения студентов и сохраняет в базу данных
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
        """
        Скачивает со степика ОДИН  КУРС и добаыляе его в базу данных
        :param course_id: id курса
        :return: 1 - к курсу нет доступа, 0 - курса не существует иначе степы
        """
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
        """
        Скачивает секции со степика  и добавляет их базу данных
        :param sections_id: список id секции
        :return: список степов
        """
        sections = self.stepic_api.sections(sections_id, attribute=['id', 'title', 'units', 'course'])
        units_id = [u for s in sections.values() for u in s['units']]
        units, steps = self.create_units_lessons(units_id)

        for s in sections.values():
            s['lessons'] = [units[u]['lesson'] for u in s['units']]
            s.pop('units')
            Section(**s).save()
        return steps

    def create_units_lessons(self, units_id):
        """
        Скачивает юниты и уроки со степика и добавляет уроки в азу данных
        :param units_id: список id юнитов
        :return: список юнитов, список степов
        """
        units = self.stepic_api.units(units_id, attribute=['lesson', 'section'])
        lessons_id = [u['lesson'] for u in units.values()]
        lessons = self.stepic_api.lessons(lessons_id, attribute=['id', 'title', 'steps'])
        steps_id = []
        for u in units.values():
            steps_id.extend(lessons[u['lesson']]['steps'])

            Lesson(section=u['section'], **(lessons[u['lesson']])).save()

        steps_id = self.create_steps(steps_id)
        return units, steps_id

    def create_steps(self, steps_id):
        """
        Скачивает степы со степика, отбирает степы-задачи и добавляет в базу данных
        :param steps_id: список id степов
        :return: список стетов - задач
        """
        steps = self.stepic_api.steps(steps_id, attribute=['id', 'position', 'actions', 'lesson'])
        # удаляем временную информацию
        for k, v in steps.items():
            if 'submit' not in v['actions']:
                Lesson.objects.with_id(v['lesson']).update(pull__steps=k)
                steps_id.remove(k)
            else:
                v.pop('actions')
                # добавляем в базу
                Step(**v).save()
        return steps_id

    def create_progress(self):
        """
        Создает прогресс студентов, добавляет в базу данных
        Создает прогресс степа (количество решивших студентов)
        :return: None
        """
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

        for sp in Step.objects.all():
            sp.update(count_passed=Grade.objects.filter(student__in=self.students, step=sp.id, is_passed=True).count())

    def get_correct_wrong_sol_date(self, solutions):

        """
        Получает дату правильного и неправильного решений
        :param solutios: список решений - list(dict)
        :return: correct_date, wrong_date - str
        """
        correct_date = None
        wrong_date = None
        if solutions:
            if solutions[0]['status'] == 'wrong':
                wrong_date = solutions[0]['time']
                wrong_date= datetime.strptime(wrong_date, '%Y-%m-%dT%H:%M:%SZ')
                try:
                    correct_date = next(filter(lambda x: x['status'] == 'correct', solutions))['time']
                    correct_date=datetime.strptime(correct_date, '%Y-%m-%dT%H:%M:%SZ')
                except:
                    pass
            else:
                correct_date = solutions[0]['time']
                correct_date = datetime.strptime(correct_date, '%Y-%m-%dT%H:%M:%SZ')

                try:
                    wrong_date = next(filter(lambda x: x['status'] == 'wrong', solutions))['time']
                    wrong_date = datetime.strptime(wrong_date, '%Y-%m-%dT%H:%M:%SZ')
                except:
                    pass
        return correct_date, wrong_date

    # выдача инфы для отображения

    def get_progress_table(self):
        """
        Возвращает информауию для заполнения информации для запонения сводной таблицы
        :return: list( mongo_model.Student() ), list( mongo_model.Course() )
        """
        # создаем список курсов и студентов
        courses = Course.objects.exclude('sections').filter(id__in=self.courses)
        students = Student.objects.only('id', 'name_google', 'progress_courses').filter(id__in=self.students)
        return students, courses

    def get_student_page(self, student_id):
        """
        Возвращает данные для заполнения страницы о студентах
        :param course_id: id курса - int
        :return: mongo_model.Student(), list( mongo_model.Course() ), Section, Lesson, Step, Grade
        """
        st = Student.objects.with_id(student_id)
        co = Course.objects.filter(id__in=self.courses)

        return st, co, Section, Lesson, Step, Grade

    def get_course_page(self, course_id):
        """
        Возвращает данные для заполнения страницы о курсах
        :param course_id: id курса - int
        :return: list( mongo_model.Student() ) ,mongo_model.Course(), Section, Lesson, Step, Grade
        """
        st = Student.objects.filter(id__in=self.students).all()
        co = Course.objects.with_id(course_id)
        return st, co, Section, Lesson, Step, Grade

    def get_start_page(self):
        """
        Возвращает информацию о пользователе
        """
        return self.loaded,self.user,self.config,self.incorrect

if __name__ == "__main__":
    a = InformationsProcessor()
    a.create_config()
    # a.stepic_api.load_token()
    # a.main_1()
    # a.students = [59934516, 19671119, 19618699, 19679512, 19618655, 2686236]
    # a.courses = [37059]
    # a.get_course_page(37059)
