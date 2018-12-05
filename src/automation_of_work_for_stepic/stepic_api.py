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

        self.MAX_IDS=10

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
            print(f"Error: load client: path {path} not found")
            return None, None

        with open(path) as f:
            data = json.load(f)

        if data:
            return data.get('client_id'), data.get('client_secret')

        print(f"Error: client id: file {path} has wrong structure")
        return None, None

    def get_url_authorize(self, redirect_uri: str):
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
            print("Error: init token: get token error")

    def clear_token(self):
        """
        Выход пользователя, очистка токена
        :return:
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
            print(f"Error: load client: path {path} not found")
            return None, None

        with open(path) as f:
            data = json.load(f)

        if data:
            return data.get('client_id'), data.get('client_secret')

        print(f"Error: client id: file {path} has wrong structure")
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
            (f"Error: load token: file {os.path.join(path,'token.json')} has wrong structure")
            return False

    def save_token(self, path: str = os.path.join('instance')):
        """
        Созраняет токен в файл  с именем token.json
        :param path: путь куда токен созранитьмя
        :return:
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

    def create_query_string_ids(self,ids):
        """
        Создает строку запроса для нескольких id
        :param ids: ids  - list
        :return: query string - str
        """
        template = '&ids[]={}'
        return '?'+(template*len(ids)).format(*ids)[1:]


    def current_user(self):
        """
        Возвращает информацию о текущем толькователе
        :return:
        """

        res = requests.get(self.url_api + 'stepics/1', headers=self._headers)
        if res.status_code < 300:
            return res.json()['users'][0]
        else:
            print("Error: download current user: status code",res.status_code)

    def current_user_id(self):
        """
        Получение информации о пользователе.
        Если id не передан, то возвращается информация о текущем пользователе
        :param id:
        :return:
        """
        res=self.current_user()

        if not res:
            return None
        return res['id']

    def get_user_name(self, id=None):
        """
        Вовзращает список full_name-ов для пользователей если id передается
        Если id не передается, возвращается full_name текущего пользотеля
        :param id: список id или один id пользователей
        :return: dict(id:name)
        """
        if not id:

            user=self.current_user()
            if not self.current_user():
                return
            return user['full_name']
        else:
            if type(id) is str:
                try:
                    user = requests.get(self.url_api + 'users/' + str(id)).json()['users'][0]
                    return user['full_name']
                except:
                    return None
            else:
                names_dict=dict.fromkeys(id,None)
                for i in range(0,len(id),self.MAX_IDS):
                    part_list=id[i:i+self.MAX_IDS]
                    try:
                        users = requests.get(self.url_api + 'users' + self.create_query_string_ids(part_list)).json()['users']
                        names_dict.update({str(user['id']):user['full_name'] for user in users})
                    except:
                        print("Error requests users")
                return names_dict


    def download_user(self, ids):
        """
        возвращающает json или список json-ов пользователей с id
        api: https://stepik.org/api/users/ID
        :param id: список id или один id пользователей
        :return: список json-ов или json пользотелей
        """
        if type(ids) is str:
            with open(ids + ".json", "w") as f:
                json.dump(self.get_user_name(ids), f, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            for id in ids:
                with open(id + ".json", "w") as f:
                    json.dump(self.get_user_name(id), f, indent=4, sort_keys=True, ensure_ascii=False)

    def get_course_name(self, id):
        """
        возвращает title курса
        api: https://stepik.org/api/courses/
        :param id: список id или один id курса
        :return: title курса
        """
        if type(id) is str:
            try:
                a = requests.get(self.url_api + 'courses/' + str(id), headers=self._headers)
                course = a.json()['courses'][0]
                return course['title']
            except Exception as e:
                print('Error get_course_name id =', id, e)
                return None
        else:
            courses_titles = []
            for course_id in id:
                try:
                    course = \
                    requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()['courses'][0]
                    courses_titles.append(course['title'])
                except Exception as e:
                    print(e)
                    courses_titles.append(None)
            return courses_titles

    def get_course_statistic(self, id):
        """
        возвращающает json или список json-ов со статистикой о курсе
        api: https://stepik.org/api/course-grades?course=ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """
        try:
            grades = requests.get(self.url_api + 'course-grades?course=' + str(id), headers=self._headers).json()[
                'course-grades']
            return grades
        except Exception as e:
            print('Error get_course_statistic id = ', id, e)
            return None

    def course_structure(self, course_id):
        """
        Получает информацию о структуре курса
        :param course_id: str - индекс курса
        :return: список секций/модулей курса
        """
        try:
            course = requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()["courses"][0]
            return [self.section_structure(section_id) for section_id in course['sections']]
        except Exception as e:
            print(f"Error in function course_structure(course_id={course_id})\n\t{e}")

    def section_structure(self, section_id):
        """
        Получает информацию о секции/модуле курса
        :param section_id: str - индекс секции/модуля
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

    def unit_structure(self, unit_id):
        """
        Получает информацию о блоке
        :param unit_id: str - индекс блока
        :return: {}, содержащий информацию об уроке блока
        """
        try:
            unit = requests.get(self.url_api + 'units/' + str(unit_id), headers=self._headers).json()['units'][0]
            return self.lesson__structure(str(unit['lesson']))
        except Exception as e:
            print(f"Error in function unit_structure(unit_id={unit_id})\n\t{e}")

    def lesson__structure(self, lesson_id):
        """
        Получает информацию об уроке
        :param lesson_id: str - индекс урока
        :return: {}, содержащий информацию об уроке блока
        """
        try:
            lesson = requests.get(self.url_api + 'lessons/' + str(lesson_id), headers=self._headers).json()['lessons'][0]
            return {
                "title": lesson['title'],
                "id": str(lesson['id']),
                "steps": [str(i) for i in lesson['steps']]
            }
        except Exception as e:
            print(f"Error in function lesson__structure(lesson_id={lesson_id})\n\t{e}")

    def get_date_of_first_correct_sol(self, step_id):
        """
        Принимает на вход id степа и возвращает дату первого удачного решения в формате datetime
        :param step_id: id степа
        :return: datetime object - дата первого удачного решения
        """
        try:
            step_submissions = \
            requests.get(self.url_api + 'submissions?status=correct&step=' + str(step_id) + '&order=asc',
                         headers=self._headers).json()['submissions']
            if len(step_submissions) != 0:
                date = datetime.strptime(str(step_submissions[0]['time']), '%Y-%m-%dT%H:%M:%SZ')
                return date
            else:
                return None
        except:
            print(f"Error in function get_date_of_first_correct_sol(step_id={step_id})")

    def get_date_of_first_wrong_sol(self, step_id):
        """
        Принимает на вход id степа и возвращает дату первого неудачного решения в формате datetime
        :param step_id: id степа
        :return: datetime object - дата первого неудачного решения
        """
        try:
            step_submissions = \
            requests.get(self.url_api + 'submissions?status=wrong&step=' + str(step_id) + '&order=asc',
                         headers=self._headers).json()['submissions']
            if len(step_submissions) != 0:
                date = datetime.strptime(str(step_submissions[0]['time']), '%Y-%m-%dT%H:%M:%SZ')
                return date
            else:
                return None
        except:
            print(f"Error in function get_date_of_first_wrong_sol(step_id={step_id})")

    def get_date_of_first_correct_sol_for_student(self, step_id, student_id):
        """
        Возвращает дату первого удачного решения степа студентом
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
                return None
        except:
            print(
                f"Error in function get_date_of_first_correct_sol_for_student(step_id={step_id}, student_id={student_id})")

    def get_date_of_first_wrong_sol_for_student(self, step_id, student_id):
        """
        Возвращает дату первого неудачного решения степа студентом
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
                return None
        except:
            print(
                f"Error in function get_date_of_first_wrong_sol_for_student(step_id={step_id}, student_id={student_id})")

    def get_date_of_sol_for_student(self, step_id, student_id):
        """
        Возвращает дату первого неудачного решения степа студентом
        :param step_id: id степа
        :param student_id: id студента
        :return: datetime object - дата первого неудачного решения студента
        """
        try:
            step_submissions = requests.get(
                self.url_api + 'submissions?&step=' + str(step_id) + '&user=' + str(
                    student_id) + '&order=asc', headers=self._headers).json()['submissions']
            if len(step_submissions) != 0:
                date = datetime.strptime(str(step_submissions[0]['time']), '%Y-%m-%dT%H:%M:%SZ')
                return date
            else:
                return None
        except:
            print(
                f"Error in function get_date_of_first_wrong_sol_for_student(step_id={step_id}, student_id={student_id})")

    def course(self,course_id,attribute=['id','title','sections','actions']):
        """
        Возвращает информацию о курсe
        """
        try:
            course = requests.get(self.url_api + 'courses' + self.create_query_string_ids([course_id]) ,headers=self._headers).json()['courses']
        except:
            print("Error requests users")

        if course:
            return {attr: course[0][attr] for attr in attribute}


    def sections(self,ids,attribute=['id','title','units']):
        sections_dict = dict.fromkeys(ids, None)
        for i in range(0, len(ids), self.MAX_IDS):
            part_list = ids[i:i + self.MAX_IDS]
            try:
                sections = requests.get(self.url_api + 'sections' + self.create_query_string_ids(part_list),
                                       headers=self._headers).json()['sections']

                sections_dict.update(
                    {section['id']: {attr: section[attr] for attr in attribute} for section in sections})
            except:
                print("Error requests users")
        return sections_dict

    def units(self,ids):
        units_dict = dict.fromkeys(ids, None)
        for i in range(0, len(ids), self.MAX_IDS):
            part_list = ids[i:i + self.MAX_IDS]
            try:
                units = requests.get(self.url_api + 'units' + self.create_query_string_ids(part_list),
                                       headers=self._headers).json()['units']

                units_dict.update(
                    {unit['id']: unit['lesson'] for unit in units})
            except:
                print("Error requests users")
        return units_dict

    def lessons(self,ids,attribute=['id','title','steps']):
        lessons_dict = dict.fromkeys(ids, None)
        for i in range(0, len(ids), self.MAX_IDS):
            part_list = ids[i:i + self.MAX_IDS]
            try:
                lessons = requests.get(self.url_api + 'lessons' + self.create_query_string_ids(part_list),
                                       headers=self._headers).json()['lessons']

                lessons_dict.update(
                    {lesson['id']: {attr: lesson[attr] for attr in attribute} for lesson in lessons})
            except:
                print("Error requests users")
        return lessons_dict


    def steps(self,ids,attribute=['id','position','actions']):
        steps_dict = dict.fromkeys(ids, None)
        for i in range(0, len(ids), self.MAX_IDS):
            part_list = ids[i:i + self.MAX_IDS]
            try:
                steps = requests.get(self.url_api + 'steps' + self.create_query_string_ids(part_list),
                                       headers=self._headers).json()['steps']

                steps_dict.update(
                    {step['id']: {attr: step[attr] for attr in attribute} for step in steps})
            except:
                print("Error requests users")
        return steps_dict

if __name__ == '__main__':
    a = StepicAPI()
    a.load_token()
    print(a.courses(['37059','1','123456','2345678987654']))

