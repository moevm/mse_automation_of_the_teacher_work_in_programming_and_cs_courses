# mse_automation_of_the_teacher_work_in_programming_and_cs_courses
Запуск приложения:
1) Установить модули из файла requirements.txt
2) Создать приложение stepic (https://stepik.org/oauth2/applications/) с параметрами: Client type – confidential; Authorization Grant Type - authorization-code; Redirect Uris - http://127.0.0.1:5000/auth/login
3) Создать файл /stepic_client.json из файла stepic_client.json.example заполнив поля "client_id" and "client_secret" 
4) Запросить у участника проекта доступ к google api (получить токен) и поместить в папку resources
5) Запустить приложение с помощью run.bat/run.sh
