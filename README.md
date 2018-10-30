# mse_automation_of_the_teacher_work_in_programming_and_cs_courses
## Запуск приложения:
1. Установить модули из файла requirements.txt
2. Создать приложение stepiс:
   1. Перейти на https://stepik.org/oauth2/applications/
   2. Создать приложение с параметрами: 
    Client type – confidential;
    Authorization Grant Type - authorization-code;
    Redirect Uris - http://127.0.0.1:5000/auth/login
   3. Скопировать "client_id" и "client_secret"
3. Создать файл /stepic_client.json из файла stepic_client.json.example заполнив поля "client_id" and "client_secret" 
4. Запросить у участника проекта доступ к google api (получить токен) и поместить в папку resources
5. Запустить приложение с помощью run.bat/run.sh
## Презентации
[Этап1](https://github.com/moevm/mse_automation_of_the_teacher_work_in_programming_and_cs_courses/raw/master/%D0%9F%D1%80%D0%BE%D0%B5%D0%BA%D1%824_%D0%AD%D1%82%D0%B0%D0%BF1.pptx)
