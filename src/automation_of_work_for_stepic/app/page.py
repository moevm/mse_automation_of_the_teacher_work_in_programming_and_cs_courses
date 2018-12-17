from flask import (
    Blueprint, render_template
)
import json

from automation_of_work_for_stepic.information_processor2 import InformationsProcessor
from automation_of_work_for_stepic.app.auth import login_required, stepic

bp = Blueprint('page', __name__)
get_info = InformationsProcessor()


@bp.route('/')
@login_required
def index():
    # a = get_info.create_students()
    # b = get_info.create_courses()
    # c = get_info.create_course_grades()
    # get_info.add_course_structures()
    # get_info.add_info_about_students()
    students, courses = get_info.get_progress_table()
    return render_template('page/index.html', students=students, courses=courses)


@bp.route('/start')
def start_page():
    return render_template('page/start.html')


@bp.route('/students/<int:id>')
@login_required
def student_page(id: int):
    if id in get_info.students:
        student, courses, Section, Lesson, Step, Grade = get_info.get_student_page(id)
        return render_template('page/student.html', student=student, courses=courses, Section=Section, Lesson=Lesson,
                               Step=Step, Grade=Grade)
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id: int):
    if id in get_info.courses:
        students, course, Section, Lesson, Step, Grade = get_info.get_course_page(id)
        return render_template('page/course.html', students=students, course=course, Section=Section, Lesson=Lesson,
                               Step=Step, Grade=Grade)
    else:
        return render_template('error/404.html')
