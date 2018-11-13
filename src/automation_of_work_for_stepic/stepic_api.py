import json
import os
import requests

from automation_of_work_for_stepic.utility import singleton

def get_current_user(token):
    res = requests.get('https://stepik.org/api/stepics/1', header=f'Authorization: Bearer {token}')

@singleton
class StepicAPI:
    def __init__(self, file_client=os.path.join('resources','stepic_client.json')):
        self.url_api = 'https://stepik.org/api/'
        self.url_auth = "https://stepik.org/oauth2/"
        self.client_id, self.client_secret = self.load_client(file_client)
        self.response_token = None
        self.token = None
        self.token_type = None
        self.current_user = None

    def get_url_authorize(self, redirect_uri:str):
        """
        Возвращает ссылку для регистрации на степике
        :param redirect_uri:  ссылк на адрес, который получит код авторизации
        :return:
        """
        return self.url_auth + f'authorize/?response_type=code&client_id={self.client_id}&redirect_uri={redirect_uri}'

    def init_token(self, code:str, redirect_uri:str):
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
        Выход пользователя
        :return:
        """
        self.response_token = None
        self.token = None
        self.token_type = None
        self.current_user = None

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
        if not os.path.exists(os.path.join(path,'token.json')):
            print(f"Error: load token: path {path} not found")
            return False

        with open(os.path.join(path,'token.json'),'r') as f:
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
        Созраняет токен в файл
        :param path:
        :return:
        """
        print(self.response_token)
        if path:
            with open(os.path.join(path,'token.json'), 'w') as outfile:
                json.dump(self.response_token, outfile)

    @property
    def _headers(self):
        return {'Authorization': self.token_type + ' ' + self.token}

    def download_current_user(self):
        """
        Загрузка информации о текущем пользователе
        :return:
        """
        if not self.token:
            print("Error: download current user: token don't exist")
            return

        res = requests.get(self.url_api + 'stepics/1', headers=self._headers)
        if res.status_code < 300:
            self.current_user = res.json()['users']
        else:
            print("Error: download current user: status code",res.status_code)

    def get_user_id(self, id=None):
        """
        Получение информации о пользователе.
        Если id не передан, то возвращается информация о текущем пользователе
        :param id:
        :return:
        """
        if not id:
            if not self.current_user:
                self.download_current_user()

                if not self.current_user:
                    return None

            return self.current_user[0]['id']
        else:
            pass

    def get_user_name(self, id=None):
        """
        Вовзращает список full_name-ов для пользователей если id передается
        Если id не передается, возвращается full_name текущего пользотеля
        :param id: список id или один id пользователей
        :return: list[full_name]
        """
        if not id:

            if not self.current_user:
                self.download_current_user()
                if not self.current_user:
                    return
            return self.current_user[0]['full_name']
        else:
            if type(id) is str:
                print("1")
                try:
                    user = requests.get(self.url_api + 'users/' + str(id)).json()['users'][0]
                    return user['full_name']
                except:
                    return None
            else:
                students_fn = []
                for user_id in id:
                    try:
                        user = requests.get(self.url_api + 'users/' + str(user_id)).json()['users'][0]
                        students_fn.append(user['full_name'])
                    except:
                        students_fn.append(None)
                return students_fn

    def download_user(self, ids):
        """
        возвращающает json или список json-ов пользователей с id
        api: https://stepik.org/api/users/ID
        :param id: список id или один id пользователей
        :return: список json-ов или json пользотелей
        """
        if type(ids) is str:
            with open(ids+".json", "w") as f:
                json.dump(self.get_user_name(ids), f, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            for id in ids:
                with open(id+".json", "w") as f:
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
                course=a.json()['courses'][0]
                return course['title']
            except Exception as e:
                print(e)
                return None
        else:
            courses_titles = []
            for course_id in id:
                try:
                    course = requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()['courses'][0]
                    courses_titles.append(course['title'])
                except Exception as e:
                    print(e)
                    courses_titles.append(None)
            return courses_titles

    """
        def get_course_learners_count(self, id):
            try:
                course = requests.get(self.url_api  + 'courses/' + str(id), headers=self._headers).json()['courses'][0]
                return course['learners_count']
            except:
                return None
            pass

        def get_course_certificates_count(self, id):
            try:
                course = requests.get(self.api_url + 'courses/' + str(id), headers=self._headers).json()['courses'][0]
                return course['certificates_count']
            except:
                return None
            pass

        def get_course_score(self, course_id, user_id):

            Возвращает прогресс пользователя на курсе (кол-во полученных баллов)
            :param self:
            :param course_id: id курса
            :param user_id: id пользователя
            :return: кол-во баллов

            try:
                course = requests.get(self.api_url + + 'course-grades?course=' + str(course_id)  + '&user=' + str(user_id), headers=self._headers).json()['course-grades'][0]
                return course['score']
            except:
                return None

            pass
    """

    def get_course_statistic(self, id):
        """
        возвращающает json или список json-ов со статистикой о курсе
        api: https://stepik.org/api/course-grades?course=ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """
        try:
            grades = requests.get(self.url_api + 'course-grades?course=' + str(id), headers=self._headers).json()['course-grades']
            return grades
        except Exception as e:
            print(e)
            return None


    def course_info_to_json(self, id):
        """
        Сохраняет информацию по курсу(ам) в json(-ы)
        :param id: str/[str] - индекс / список индексов курса
        :return: True/False - успешная/неуспешная запись
        """
        try:
            if type(id) is str:
                with open(os.path.join("instance", str(id)+"_info.json"), "w") as js:
                    json.dump(self.get_course_info(id), js, indent=4, sort_keys=True, ensure_ascii=False)
            else:
                for course_id in id:
                    with open(os.path.join("instance", str(course_id)+"_info.json"), "w") as js:
                        json.dump(self.get_course_info(course_id), js, indent=4, sort_keys=True, ensure_ascii=False)
            return True
        except:
            return False

    def get_course_info(self, course_id):
        """
        Получает информацию о курсе (структура курса)
        :param course_id: str - индекс курса
        :return: {}, содержащий название, id и список секций/модулей курса
        """
        try:
            course = requests.get(self.url_api + 'courses/' + str(course_id), headers=self._headers).json()["courses"][0]
            info_sections = []
            for section_id in course['sections']:
                info_sections.append(self.get_section_info(section_id))
            return {
                "title": course['title'],
                "id": course['id'],
                "sections of course": info_sections
            }
        except:
            print(f"Error in function get_course_info(course_id={course_id})")

    def get_section_info(self, section_id):
        """
        Получает информацию о секции/модуле курса
        :param section_id: str - индекс секции/модуля
        :return: {}, содержащий название, id и список уроков секции/модуля
        """
        try:
            section = requests.get(self.url_api + 'sections/' + str(section_id), headers=self._headers).json()['sections'][0]
            lessons = []
            for unit_id in section['units']:
                lessons.append(self.get_unit_info(unit_id))
            return {
                "title": section['title'],
                "id": section['id'],
                "lessons of section": lessons
            }
        except:
            print(f"Error in function get_section_info(section_id={section_id})")

    def get_unit_info(self, unit_id):
        """
        Получает информацию о блоке
        :param unit_id: str - индекс блока
        :return: {}, содержащий информацию об уроке блока
        """
        try:
            unit = requests.get(self.url_api + 'units/' + str(unit_id), headers=self._headers).json()['units'][0]
            return self.get_lesson_info(str(unit['lesson']))
        except:
            print(f"Error in function get_unit_info(unit_id={unit_id})")

    def get_lesson_info(self, lesson_id):
        """
        Получает информацию об уроке
        :param lesson_id: str - индекс урока
        :return: {}, содержащий информацию об уроке блока
        """
        try:
            lesson = requests.get(self.url_api + 'lessons/' + str(lesson_id), headers=self._headers).json()['lessons'][0]
            return {
                "title": lesson['title'],
                "id": lesson['id'],
                "steps of lesson": lesson['steps']
            }
        except:
            print(f"Error in finction get_lesson_info(lesson_id={lesson_id})")


if __name__ == '__main__':
    a = StepicAPI()
    a.load_token('C:\\Users\\nosov\PycharmProjects\\autocheck_stepic\\src\\instance')
    b=a.get_course_statistic('37059')
    print(b)
    for m in b:
        for k,v in m.items():
            print(k,':',v)
            if type(v) == type({}):
                for k1, v2 in v.items():
                    print('\t',k1, ':', v2)
        #if type(v) == type([]):
        #    for i in v:
        #        print(i)

