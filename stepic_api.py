import requests
import json
import os


def get_current_user(token):
    res = requests.get('https://stepik.org/api/stepics/1', header=f'Authorization: Bearer {token}')


class StepicAPI:
    def __init__(self, file_client='stepic_client.json'):
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
            print("Error: load client: path not found")
            return None, None

        with open(path) as f:
            data = json.load(f)

        if data:
            return data.get('client_id'), data.get('client_secret')

        print(f"Error: client id: file {path} has wrong structure")
        return None, None

    def load_token(self, path: str = os.path.join('instance','token.json')):
        """
        Загружает токен из файла. Если загрузка удалась, то возращает True, инача - False
        :param path: путь к токену
        :return: Bool
        """
        if not os.path.exists(path):
            print("Error: load token: path not found")
            return False

        with open(path,'r') as f:
            data = json.load(f)

        if data and 'access_token' in data and 'token_type' in data:
            self.response_token = data
            self.token = data['access_token']
            self.token_type = data['token_type']
            return True
        else:
            (f"Error: load token: file {path} has wrong structure")
            return False

    def save_token(self, path: str = os.path.join('instance','token.json')):
        """
        Созраняет токен в файл
        :param path:
        :return:
        """
        print(self.response_token)
        if path:
            with open(path, 'w') as outfile:
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
        Вовзращает список dict-ов c last_name и first_name для пользователей если id передается
        Если id не передается, возвращается full_name текущего пользотеля
        :param id: список id или один id пользователей
        :return: list[dict]
        """
        api_url = "https://stepik.org/api/"
        if not id:

            if not self.current_user:
                self.download_current_user()
                if not self.current_user:
                    return
            return self.current_user[0]['full_name']
        else:
         students_fn = []
         if type(id) is str:
                user = requests.get(api_url + 'users/' + str(id)).json()['users'][0]
                students_fn.append({user['last_name']: user['first_name']})
         else:
                for user_id in id:
                    user = requests.get(api_url + 'users/' + str(user_id)).json()['users'][0]
                    students_fn.append({user['last_name']: user['first_name']})
         return students_fn

    def download_user(self, id):
        """
        возвращающает json или список json-ов пользователей с id
        api: https://stepik.org/api/users/ID

        :param id: список id или один id пользователей
        :return: список json-ов или json пользотелей
        """
        pass

    def get_course_statistic(self, id):
        """
        возвращающает json или список json-ов со статистикой о курсе
        api: https://stepik.org/api/course-grades?course=ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """

        pass

    def get_course_info(self, id):
        """
        возвращающает json или список json-ов с информацией курсе
        api: https://stepik.org/api/courses/ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """
        pass
