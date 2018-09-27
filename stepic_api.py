import requests


def get_current_user(token):
    res = requests.get('https://stepik.org/api/stepics/1', header=f'Authorization: Bearer {token}')


class StepicAPI:
    def __init__(self):
        self.url_api = 'https://stepik.org/api/'
        self.url_auth = "https://stepik.org/oauth2/"
        self.client_id = "vXmDt0jmKqcOZvh4HcdR6wFz47m3S2SrY4t9gdxU"
        self.client_secret = "Kw8gI1WaPLLJ3b4pHAwwSmsDJT8PYkBRaA91Vbsyf1MvwGUHbILbMTpOaVUhIC2S5FAflE3rfjEhYPohSm0uV01yGlChtfV4dwE4HlBmbrN3zSy9q1Ziy667lECPlvbv"
        self.response_token=None
        self.token=None
        self.token_type=None
        self.current_user=None


    def get_url_authorize(self, redirect_uri):
        if self.token:
            print("Token exist")
            return

        return self.url_auth + f'authorize/?response_type=code&client_id={self.client_id}&redirect_uri={redirect_uri}'

    def init_token(self, code, redirect_uri):
        if self.token:
            print("Token exist")
            return

        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        self.response = requests.post(self.url_auth + 'token/', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }, auth=auth)
        self.token = self.response.json().get('access_token', None)
        self.token_type=self.response.json().get('token_type', None)

        if not self.token:
            print("Token error")


    def clear_token(self):
        """
        Выход пользователя
        :return:
        """
        self.response_token=None
        self.token=None
        self.token_type=None
        self.current_user=None

    @property
    def _headers(self):
        return {'Authorization': self.token_type+' ' + self.token}

    def download_currnet_user(self):
        if not self.token:
            print("Token don't exist")
            return
        res = requests.get(self.url_api + 'stepics/1', headers=self._headers)
        if res.status_code <300:
            self.current_user=res.json()

    def get_user_id(self,id=None):
        """

        :param id:
        :return:
        """
        if not id:
            if not self.current_user:
                self.download_currnet_user()

                if not self.current_user:
                    print("Error get_current_user_id")
                    return None

            try:
                res=self.current_user['users'][0]['id']
            except Exception:
                return None
            else:
                return res


    def get_user_name(self,id=None):
        """
        Вовзращает список dict-ов c last_name и first_name для пользователей если id передаетя
        Если id не передается, возвращается full_nameтекущего пользотеля
        :param id: список id или один id пользователей
        :return: list[dict]
        """
        if not id:
            if not self.current_user:
                self.download_currnet_user()

                if not self.current_user:
                    print("Error get_current_user_name")
                    return None
            try:
                res=self.current_user['users'][0]['full_name']
            except Exception:
                return None
            else:
                return res

        else:
            pass


    def download_user(self,id):
        """
        возвращающает json или список json-ов пользователей с id
        api: https://stepik.org/api/users/ID

        :param id: список id или один id пользователей
        :return: список json-ов или json пользотелей
        """
        pass


    def get_course_statistic(self,id):
        """
        возвращающает json или список json-ов со статистикой о курсе
        api: https://stepik.org/api/course-grades?course=ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """

        pass


    def get_course_info(self,id):
        """
        возвращающает json или список json-ов с информацией курсе
        api: https://stepik.org/api/courses/ID
        :param id: список id или один id курса
        :return: список json-ов или json курса
        """
        pass




