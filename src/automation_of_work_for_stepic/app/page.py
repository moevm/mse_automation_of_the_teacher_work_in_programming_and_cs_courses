from flask import (
    Blueprint, render_template,session,redirect,url_for
)
import json

from automation_of_work_for_stepic.information_processor import InformationsProcessor
from automation_of_work_for_stepic.app.auth import login_required

bp = Blueprint('page', __name__)

get_info=InformationsProcessor()

@bp.route('/progress')
@login_required
def progress():
    get_info = InformationsProcessor()
    #get_info = session.get('processor')
    if get_info:
        students, courses = get_info.get_progress_table()
        return render_template('page/progress.html', students=students, courses=courses)
    else:
        return render_template('error/404.html')

@bp.route('/start')
@login_required
def start():
    get_info = InformationsProcessor()
    #get_info=session.get('processor')
    if get_info:
        loaded, user, config, incorrect=get_info.get_start_page()
        return render_template('page/start.html', loaded=loaded,user=user, config=config, incorrect=incorrect)
    else:
        return render_template('error/404.html')



@bp.route('/students/<int:id>')
@login_required
def student_page(id: int):
    get_info = InformationsProcessor()
    #get_info = session.get('processor')
    if get_info.loaded and id in get_info.students:
        student, courses, Section, Lesson, Step, Grade = get_info.get_student_page(id)
        return render_template('page/student.html', student=student, courses=courses, Section=Section, Lesson=Lesson,
                               Step=Step, Grade=Grade)
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id: int):
    get_info = InformationsProcessor()
    #get_info = session.get('processor')
    if get_info.loaded and id in get_info.courses:
        students, course, Section, Lesson, Step, Grade = get_info.get_course_page(id)
        return render_template('page/course.html', students=students, course=course, Section=Section, Lesson=Lesson,
                               Step=Step, Grade=Grade)
    else:
        return render_template('error/404.html')

@bp.route('/load')
@login_required
def load():
    get_info = InformationsProcessor()
    get_info.load_new()
    return  redirect(url_for('page.start'))

