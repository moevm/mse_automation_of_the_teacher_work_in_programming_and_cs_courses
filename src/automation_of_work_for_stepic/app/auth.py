import functools

from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app

from automation_of_work_for_stepic.app.db import get_db
from automation_of_work_for_stepic.stepic_api import StepicAPI

bp = Blueprint('auth', __name__, url_prefix='/auth')
stepic = StepicAPI()
redirect_uri = 'http://127.0.0.1:5000/auth/login'

@bp.route('/login')
def login():
    """
    Авторизация пользователя
    :return:
    """
    #ошибка
    error = request.args.get('error')
    #код авторищации
    code = request.args.get('code')

    #если нет ошибки и есть код
    if not error and code:
        #получаем токен
        stepic.init_token(code, redirect_uri)

        if app.config['ENV'] == 'development':
            stepic.save_token()

        #сохраняем пользователя в базу
        db = get_db()
        user_id = stepic.get_user_id()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (user_id,)
        ).fetchone()

        if user is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (user_id, ' '))
            db.commit()

        #очищаем ссесию
        session.clear()
        session['user_id'] = user_id
        return redirect(url_for('index'))
    else:
        return render_template('error/401.html')
        print("Error:login: get code error")


@bp.before_app_request
def load_logged_in_user():
    """
    Загрузка информации перел открытием страницы
    :return:
    """
    user_id= session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = stepic.get_user_name()

    if app.config['ENV'] == 'development':
        g.dev = True
    else:
        g.dev = None


@bp.route('/logout')
def logout():
    """
    Выход пользователя
    :return:
    """
    session.clear()
    stepic.clear_token()
    return redirect(url_for('index'))

def login_required(view):
    """
    Декоратор, проверяющий залогинен ли пользователь
    :param view:
    :return:
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template('error/401.html')

        return view(**kwargs)

    return wrapped_view

@bp.route('/login_stepic')
def login_stepic():
    """
    Авторизация пользователя через степик
    :return:
    """
    return redirect(stepic.get_url_authorize(redirect_uri))

@bp.route('/login_dev')
def login_dev():
    """
    Авторизация пользователя через степик  в режиме разработчика
    :return:
    """
    if stepic.load_token():
        # сохраняем пользователя в базу
        db = get_db()
        user_id = stepic.get_user_id()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (user_id,)
        ).fetchone()

        if user is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (user_id, ' '))
            db.commit()

        # очищаем ссесию
        session.clear()
        session['user_id'] = user_id
        return redirect(url_for('index'))
    else:
        #переходим на авторизаци степика
        return redirect(stepic.get_url_authorize(redirect_uri))