import json
import os
import requests
from datetime import datetime
from automation_of_work_for_stepic.utility import singleton


@singleton
class StepicAPI:
    """
    Класс для доступа к stepic api
    """
    def __init__(self, file_client=os.path.join('resources','stepic_client.json')):
        self.url_api = 'https://stepik.org/api/'
        self.url_auth = "https://stepik.org/oauth2/"
        self.client_id, self.client_secret = self.load_client(file_client)

        self.response_token = None
        self.token = None
        self.token_type = None

    def load_client(self, path: str):
        """
        Получение данных клиента для взаимодействия с апи

        :param file: путь к файлу
        :return: (client_id, secret_key)
        """
        if not os.path.exists(path):
            print(f"Error in function load_client: path {path} not found")
            return None, None

        with open(path) as f:
            data = json.load(f)

        if data:
            return data.get('client_id'), data.get('client_secret')

        print(f"Error in function load_client: file {path} has wrong structure")
        return None, None

    def url_authorize(self, redirect_uri: str):
        """
        Возвращает ссылку для регистрации на степике

        :param redirect_uri:  ссылка на адрес, который получит код авторизации
        :return: сформированный url
        """
        return self.url_auth + f'authorize/?response_type=code&client_id={self.client_id}&redirect_uri={redirect_uri}'

    def init_token(self, code: str, redirect_uri: str):
        """
        Инициализация токена по полуенному коду.

        :param code: код авторизации
        :param redirect_uri: адрес, которы получил этот код
        :return: None
        """

        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)

        self.response_token = requests.post(self.url_auth + 'token/', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }, auth=auth).json()

        self.token = self.response_token.get('access_token', None)
        self.token_type = self.response_token.get('token_type', None)

        if not self.token:
            print(f"Error in function init_token({code}, {redirect_uri}: get token error")

    def clear_token(self):
        """
        Выход пользователя, очистка токена

        :return: None
        """
        self.response_token = None
        self.token = None
        self.token_type = None

    def load_client(self, path: str):
        """
        Получение данных клиента для взаимодействия с апи

        :param file: путь к файлу
        :return: (client_id, secret_key)
        """
        if not os.path.exists(path):
            print(f"Error in function load_client: path {path} not found")
            return None, None

        with open(path) as f:
            data = json.load(f)

        if data:
            return data.get('client_id'), data.get('client_secret')

        print(f"Error in function load_client: {path} has wrong structure")
        return None, None

    def load_token(self, path: str = os.path.join('instance')):
        """
        Загружает токен из файла. Если загрузка удалась, то возращает True, инача - False

        :param path: путь к токену
        :return: Bool
        """
        if not os.path.exists(os.path.join(path, 'token.json')):
            print(f"Error: load token: path {path} not found")
            return False

        with open(os.path.join(path, 'token.json'), 'r') as f:
            data = json.load(f)

        if data and 'access_token' in data and 'token_type' in data:
            self.response_token = data
            self.token = data['access_token']
            self.token_type = data['token_type']
            return True
        else:
            (f"Error in function load_token: file {os.path.join(path,'token.json')} has wrong structure")
            return False

    def save_token(self, path: str = os.path.join('instance')):
        """
        Созраняет токен в файл  с именем token.json

        :param path: путь куда токен созранитьмя
        :return: None
        """
        print(self.response_token)
        if path:
            with open(os.path.join(path, 'token.json'), 'w') as outfile:
                json.dump(self.response_token, outfile)

    @property
    def _headers(self):
        """
        Формирует заголовок для запроса к апи

        :return: данные с токеном
        """
        if self.token:
            return {'Authorization': self.token_type + ' ' + self.token}
        return None

    def current_user(self):
        """
        Возвращение информации о текущем пользователе
        api: https://stepik.org/api/stepics/1

        :return: объект, содержащий информацию о пользователе
        """

        res = requests.get(self.url_api + 'stepics/1', headers=self._headers)
        if res.status_code < 300:
            return res.json()['users'][0]
        else:
            print(f"Error in function current_user(): download current user: status code {res.status_code}")

    def current_user_id(self):
        """
        Возвращение id текущего пользователя
        api: https://stepik.org/api/stepics/1

        :return: id текущего пользователя
        """
        res = self.current_user()

        if not res:
            return None
        return res['id']

    def user_name(self, id=None):
        """
        Вовзращение полное имя пользователя при передаче id
        и списка полных имен пользователей при передаче списка id.
        Если id не передается, возвращение полного имени текущего пользотеля
        api: https://stepik.org/api/users/ID

        :param id: список id или один id пользователей
        :return: str или list[full_name]
        """
        if not id:
            user = self.current_user()
            if not self.current_user():
                return
            return user['full_name']
        else:
            if type(id) is str:
                try:
                    user = requests.get(self.url_api + 'users/' + str(id)).json()['users'][0]
                    return user['full_name']
                except Exception as e:
                    print(f"Error in function user_name(id = {id})\n\t{e}")
                    return None
            else:
                students_fn = []
                for user_id in id:
                    try:
                        user = requests.get(self.url_api + 'users/' + str(user_id)).json()['users'][0]
                        students_fn.append(user['full_name'])
                    except Exception as e:
                        print(f"Error in function user_name\n\t{e}")
                        students_fn.append(None)
                return students_fn


    def course_title(self, id):
        """
        Получение заголовка курса
        Возвращает заголовок курса при передаче id и список заголовков курсов при передаче id курсов
        api: https://stepik.org/api/courses/ID

        :param id: список id или один id курса
        :return: заголовок курса или список заголовков курсов
        """
        if type(id) is str:
            try:
                a = requests.get(self.url_api + 'courses/' + str(id), headers=self._headers)
                course = a.json()['courses'][0]
                return course['title']
            except Exception as e:
                print(f"Error in function course_title(id = {id})\n\t{e}")
                return None
        else:
            courses_titles = []
            for course_id in id:
                try:
                    course = \
                    requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()['courses'][0]
                    courses_titles.append(course['title'])
                except Exception as e:
                    print(f"Error in function course_title\n\t{e}")
                    courses_titles.append(None)
            return courses_titles


    def course_statistic(self, id):
        """
        Возвращение json объекта со статистикой о курсе
        api: https://stepik.org/api/course-grades?course=ID

        :param id: id курса
        :return: json курса
        """
        try:
            grades = requests.get(self.url_api + 'course-grades?course=' + str(id), headers=self._headers).json()[
                'course-grades']
            return grades
        except Exception as e:
            print(f"Error in function course_statistic(id = {id})\n\t{e}")
            return None

    def course_structure(self, course_id):
        """
        Получение информации о структуре курса.
        Возвращает список секций/модулей курса
        api: https://stepik.org/api/courses/ID

        :param course_id: id курса
        :return: список секций/модулей курса
        """
        try:
            course = requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()["courses"][0]
            return [self.section_structure(section_id) for section_id in course['sections']]
        except Exception as e:
            print(f"Error in function course_structure(course_id={course_id})\n\t{e}")
            return None

    def section_structure(self, section_id):
        """
        Получение информации о секции/модуле курса
        Возвращает объект, содержащий заголовок, id и список уроков секции/модуля
        api: https://stepik.org/api/sections/ID

        :param section_id: id секции/модуля
        :return: {}, содержащий название, id и список уроков секции/модуля
        """
        try:
            section = requests.get(self.url_api + 'sections/' + str(section_id), headers=self._headers).json()['sections'][0]
            return {
                "title": section['title'],
                "id": str(section['id']),
                "lessons": [self.unit_structure(unit_id) for unit_id in section['units']]
            }
        except Exception as e:
            print(f"Error in function section_structure(section_id={section_id})\n\t{e}")
            return None

    def unit_structure(self, unit_id):
        """
        Получение информации о блоке.
        Возвращает объект, содержащий информацию об уроке блока.
        api: https://stepik.org/api/units/ID

        :param unit_id: id блока
        :return: {}, содержащий информацию об уроке блока
        """
        try:
            unit = requests.get(self.url_api + 'units/' + str(unit_id), headers=self._headers).json()['units'][0]
            return self.lesson_structure(str(unit['lesson']))
        except Exception as e:
            print(f"Error in function unit_structure(unit_id={unit_id})\n\t{e}")
            return None

    def lesson_structure(self, lesson_id):
        """
        Получение информации об уроке.
        Возвращает объект, содержащий информацию об уроке блока.
        api: https://stepik.org/api/lessons/ID

        :param lesson_id: id урока
        :return: {}, содержащий заголовок, id и список шагов урока
        """
        try:
            lesson = requests.get(self.url_api + 'lessons/' + str(lesson_id), headers=self._headers).json()['lessons'][0]
            return {
                "title": lesson['title'],
                "id": str(lesson['id']),
                "steps": [str(i) for i in lesson['steps']]
            }
        except Exception as e:
            print(f"Error in function lesson_structure(lesson_id={lesson_id})\n\t{e}")
            return None


    def date_of_first_correct_sol_for_student(self, step_id, student_id):
        """
        Возвращает дату первого удачного решения степа студентом в формате datetime.
        api: https://stepik.org/api/submissions?status=correct&step=step&user=user&order=asc

        :param step_id: id степа
        :param student_id: id студента
        :return: datetime object - дата первого удачного решения студента
        """
        try:
            step_submissions = requests.get(
                self.url_api + 'submissions?status=correct&step=' + str(step_id) + '&user=' + str(
                    student_id) + '&order=asc', headers=self._headers).json()['submissions']
            if len(step_submissions) != 0:
                date = datetime.strptime(str(step_submissions[0]['time']), '%Y-%m-%dT%H:%M:%SZ')
                return date
            else:
                print(f"Error in function date_of_first_correct_sol_for_student"
                      f"(step_id={step_id}, student_id={student_id}):\nstep_submissions is null)")
                return None
        except Exception as e:
            print(
                f"Error in function date_of_first_correct_sol_for_student"
                f"(step_id={step_id}, student_id={student_id})\n\t{e}")
            return None

    def date_of_first_wrong_sol_for_student(self, step_id, student_id):
        """
        Возвращает дату первого неудачного решения степа студентом в формате datetime.
        api: https://stepik.org/api/submissions?status=wrong&step=step&user=user&order=asc

        :param step_id: id степа
        :param student_id: id студента
        :return: datetime object - дата первого неудачного решения студента
        """
        try:
            step_submissions = requests.get(
                self.url_api + 'submissions?status=wrong&step=' + str(step_id) + '&user=' + str(
                    student_id) + '&order=asc', headers=self._headers).json()['submissions']
            if len(step_submissions) != 0:
                date = datetime.strptime(str(step_submissions[0]['time']), '%Y-%m-%dT%H:%M:%SZ')
                return date
            else:
                print(f"Error in function date_of_first_wrong_sol_for_student"
                      f"(step_id={step_id}, student_id={student_id}):\nstep_submissions is null)")
                return None
        except:
            print(
                f"Error in function date_of_first_wrong_sol_for_student"
                f"(step_id={step_id}, student_id={student_id})\n\t{e}")
            return None


if __name__ == '__main__':
    a = StepicAPI()
    a.load_token()
    print(a.course_structure('37059'))

