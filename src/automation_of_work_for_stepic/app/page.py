from flask import (
    Blueprint, render_template
)

from automation_of_work_for_stepic.InformationsProcessor import InformationsProcessor
from automation_of_work_for_stepic.app.auth import login_required,stepic



bp = Blueprint('page', __name__)
get_info=InformationsProcessor(stepic)

@bp.route('/')
@login_required
def index():
    a=get_info.create_jsons_user()
    b=get_info.create_jsons_course()
    c=get_info.course_grades()
    print(a)
    return render_template('page/index.html', names=a,course=b,progress=c)

@bp.route('/start')
def start_page():
    return render_template('page/start.html')

@bp.route('/students/<int:id>')
@login_required
def student_page(id:int):
    if str(id) in [student['id'] for student in get_info.create_jsons_user()]:
        return render_template('page/student.html')
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id:int):
    print([course['id'] for course in get_info.create_jsons_course()])
    if id in [course['id'] for course in get_info.create_jsons_course()]:
        return render_template('page/course.html')
    else:
        return render_template('error/404.html')