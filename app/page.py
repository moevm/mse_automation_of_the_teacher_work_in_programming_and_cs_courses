from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,config
)
from InformationsProcessor import InformationsProcessor

from app.auth import login_required
from app.auth import stepic
from app.all_info import *

bp = Blueprint('page', __name__)
get_info=InformationsProcessor(stepic)

@bp.route('/')
@login_required
def index():
    a=get_info.create_jsons_user()
    b=get_info.create_jsons_course()
    c=get_info.course_grades()
    return render_template('page/index.html', names=a,course=b,progress=c)

@bp.route('/start')
def start_page():
    return render_template('page/start.html')

@bp.route('/students/<int:id>')
@login_required
def student_page(id:int):
    if id_name_exist(id):
        return render_template('page/student.html')
    else:
        return render_template('error/404.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id:int):
    if id_course_exist(id):
        return render_template('page/course.html')
    else:
        return render_template('error/404.html')