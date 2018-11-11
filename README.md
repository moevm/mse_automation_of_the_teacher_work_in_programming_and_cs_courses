# mse_automation_of_the_teacher_work_in_programming_and_cs_courses
## Запуск приложения:
Перед запуском необходимо создать папку со следующими файлы:
* **stepic_client.json**: файл для доступа к stepic api <br>
2. Создать приложение stepiс:
   1. Перейти на https://stepik.org/oauth2/applications/
   2. Создать приложение с параметрами: 
    Client type – confidential; <br>
    Authorization Grant Type - authorization-code; <br>
    Redirect Uris - http://127.0.0.1:5000/auth/login <br>
   3. Скопировать "client_id" и "client_secret"
3. Создать файл *stepic_client.json* из файла *resources/stepic_client.json.example* заполнив поля "client_id" and "client_secret"

* **private key for GoogleAPI.json**: файл для доступа к google api <br>
 Запросить у участника проекта данный файл, имеющий структуру *resources/private key for GoogleAPI.json.example*
 
* **config.json**: файл с пользовательскими настройками <br>
Заполнить файл resources/config.json

**Важно!** все три файла должны быть в одной папке. <br>

Запуск приложения <br>
1. Создать виртуальное окружение myenv (https://docs.python.org/3/library/venv.html)
2. cd ../src (в папке проекта)
3. python setup.py develop (установка пакета)
4. windows - ..\myvenv\Scripts run.bat directory <br>
linux - run.sh directory <br>
directory - путь к папке содержащие необходимые файлы (описанные выше)
5. pip uninstall automation-of-work-for-stepic-distro (удаление пакета)

При возникновении ошибок при установке пакета необходимо удалить пакет и повторить установку.

## Презентации
[Этап1](https://github.com/moevm/mse_automation_of_the_teacher_work_in_programming_and_cs_courses/raw/master/Presentations/%D0%9F%D1%80%D0%BE%D0%B5%D0%BA%D1%824_%D0%AD%D1%82%D0%B0%D0%BF1.pptx)
## Демонстрация
[Этап1](https://youtu.be/miiINJJ0cvg)
## Скриншоты
[Открыть](https://github.com/moevm/mse_automation_of_the_teacher_work_in_programming_and_cs_courses/raw/master/Screenshots)
