from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,config
)

from app.auth import login_required
from app.all_info import *

bp = Blueprint('page', __name__)


@bp.route('/')
@login_required
def index():
    return render_template('page/index.html', names=get_names(),course=get_courses())

@bp.route('/start')
def start_page():
    return render_template('page/start.html')

@bp.route('/students/<int:id>')
@login_required
def student_page(id:int):
    return render_template('page/student.html')


@bp.route('/courses/<int:id>')
@login_required
def course_page(id:int):
    return render_template('page/course.html')