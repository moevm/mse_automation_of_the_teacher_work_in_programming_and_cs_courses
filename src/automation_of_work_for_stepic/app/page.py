from flask import (
    Blueprint, render_template
)
import json

from automation_of_work_for_stepic.InformationsProcessor import InformationsProcessor
from automation_of_work_for_stepic.app.auth import login_required, stepic

bp = Blueprint('page', __name__)
get_info = InformationsProcessor()


@bp.route('/')
@login_required
def index():
    a = get_info.create_students_info()
    b = get_info.create_courses_info()
    c = get_info.create_course_grades()
    return render_template('page/index.html', names=a, course=b, progress=c)


@bp.route('/start')
def start_page():
    return render_template('page/start.html')


@bp.route('/students/<int:id>')
@login_required
def student_page(id: int):
    if str(id) in [student['id'] for student in get_info.students]:
        get_info.create_info_about_student()
        info = get_info.get_student_by_id(str(id))
        return render_template('page/student.html', info=info)
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id: int):
    a = get_info.create_students_info()

    c = get_info.create_course_grades()
    b = list(c[0].values())[0]['steps'].keys()
    if str(id) in [course['id'] for course in get_info.create_courses_info()]:
        info = stepic.get_course_info(id)
        return render_template('page/course.html', info=info, names=a, steps=b, progress=c[0])
    else:
        return render_template('error/404.html')
