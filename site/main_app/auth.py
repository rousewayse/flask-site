import functools

from flask import (
    Blueprint, 
    flash,
    g, 
    redirect, 
    render_template, 
    request, 
    session, 
    url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from main_app.database import get_db

from main_app.err_messages import *

bp = Blueprint('auth', __name__, url_prefix='/auth')

# No register func now

@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        err = None

        if not username:
            err = username_required_err()
        elif not password:
            err = password_required_err()

        if err is None:
            try:
                db.execute(
                    'INSERT INTO user (username, pass_hash) VALUES (?, ?)', 
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                err = username_already_in_use_err()
            else:
                return redirect(url_for('auth.login'))
        flash(err)
    return render_template('auth/register.html')


@bp.route('/login', methods =  ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        err = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username, )
        ).fetchone()
        if user is None:
            err = invalid_username_err()
        elif not check_password_hash(user['pass_hash'], password):
            err = invalid_password_err()
        elif user['active'] == False:
            err = user_is_not_active_err()
        if err is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(err)
    return render_template('auth/login.html')


#loading user data 
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        admin = db.execute('SELECT * FROM stuff WHERE user_id = ?', (user_id,)).fetchone()
        if admin and admin['user_id'] == g.user['id']:
            g.is_admin = True
        
        teacher = db.execute('SELECT * FROM teachers WHERE user_id = ?', (user_id,)).fetchone()
        if teacher and teacher['user_id'] == g.user['id']:
            g.is_teacher = True
        else:
            g.is_teacher = False
        if g.user['active'] == False:
            g.pop('user', None)
            session.clear()

#setting up login required decorator

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view



@bp.route('/logout')
#@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))




