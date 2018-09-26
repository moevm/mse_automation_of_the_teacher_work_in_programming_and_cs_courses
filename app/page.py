from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db
from app.all_info import *

bp = Blueprint('page', __name__)

@bp.route('/')
def index():
    return render_template('page/index.html', name=get_name(),course=get_course())
