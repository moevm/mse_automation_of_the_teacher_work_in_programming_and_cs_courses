from flask import (
    Blueprint, render_template
)
import json

from automation_of_work_for_stepic.InformationsProcessor import InformationsProcessor
from automation_of_work_for_stepic.app.auth import login_required, stepic

bp = Blueprint('page', __name__)
get_info = InformationsProcessor(stepic)


@bp.route('/')
@login_required
def index():
    a = get_info.create_jsons_user()
    # print(a)
    b = get_info.create_jsons_course()
    print(b)
    c = get_info.course_grades()
    # print(c)
    return render_template('page/index.html', names=a, course=b, progress=c)


@bp.route('/start')
def start_page():
    return render_template('page/start.html')


@bp.route('/students/<int:id>')
@login_required
def student_page(id: int):
    if str(id) in [student['id'] for student in get_info.create_jsons_user()]:
        #course_id = [course['id'] for course in get_info.create_jsons_course()]
        #a = get_info.info_about_students([str(id)], course_id)
        #print(a)
        with open('C:\\Users\\nosov\PycharmProjects\\autocheck_stepic\\src\\resources\\full_info.json', 'r',encoding='utf-8') as f:
            info = json.load(f)
        return render_template('page/student.html',info=info[0])
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id: int):
    #print([course['id'] for course in get_info.create_jsons_course()])
    if str(id) in [course['id'] for course in get_info.create_jsons_course()]:
        return render_template('page/course.html')
    else:
        return render_template('error/404.html')
