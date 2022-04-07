import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for
)
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort
from main_app.auth import login_required
from main_app.database import get_db

from main_app.err_messages import *
bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/<int:id>', methods=['GET'])
@login_required
def profile_info(id = None):
    db  = get_db()
    if id is None:
        abort('404')
    user_info = db.execute(f'SELECT * FROM user_info WHERE user_id = {id}' ).fetchone()
    if user_info is not  None:
        user_info = dict(user_info)
    
    as_student_info = db.execute(f'SELECT groups.title group_title, faculty.title AS faculty_title, students.cource AS cource, students.directory AS directory, students.degree AS degree, students.form AS form, students.fee AS fee  FROM students LEFT JOIN groups ON students.group_id = groups.id LEFT JOIN faculty ON faculty.id = groups.faculty_id WHERE students.user_id = {id}').fetchone()
    if as_student_info is not None:
        as_student_info = dict(as_student_info)
    
    as_teacher_info = db.execute(f'SELECT teachers.degree AS degree, faculty.title AS faculty_title FROM teachers LEFT JOIN faculty ON teachers.faculty_id = faculty.id WHERE teachers.user_id = {id}').fetchone()
    if as_teacher_info is not None:
        as_teacher_info = dict(as_teacher_info)

    if g.user['id'] != id and not g.is_admin:
        g.not_me = True
    return render_template('profile/profile.html', user_info = user_info, as_student_info = as_student_info, as_teacher_info=as_teacher_info)
