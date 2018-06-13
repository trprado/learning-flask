import functools

from flask import (
    Blueprint, flash, g,
    redirect, render_template,
    request, session, url_for
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        db = get_db()
        error = None
        
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not name:
            error = 'Name is required.'
        elif db.execute(
            'select id from user where email = ?', (email,)
        ).fetchone() is not None:
            error = 'Email {} is already registered.'.format(email)

        if  error is None:
            db.execute(
                'insert into user (email, password, name) values (?,?, ?)',
                (email, generate_password_hash(password), name)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'select * from user where email = ?',
            (email,)
        ).fetchone()

        print(password)

        if email is None:
            error = 'Incorrect email or password.'
        elif user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect email or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'select * from user where id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view