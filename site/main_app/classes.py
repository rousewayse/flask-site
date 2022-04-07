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
bp = Blueprint('classes', __name__, url_prefix='/classes')

@bp.route('/', methods=['GET'])
@login_required
def classes():
    db = get_db()
    classes = None
    if g.is_teacher == False:
        classes = db.execute('SELECT classes.title AS title, teachers.user_id AS teacher_id, user_info.fst_name AS teacher_fname, user_info.snd_name AS teacher_sname,  user_info.thrd_name AS teacher_thname FROM classes LEFT JOIN teachers ON teachers.id = classes.teacher_id LEFT JOIN students ON students.group_id = classes.group_id  LEFT JOIN user_info on user_info.user_id = teachers.user_id WHERE students.user_id = ?', (g.user['id'],)).fetchall()
    else:
        teacher = db.execute('SELECT * FROM teachers WHERE teachers.user_id = ?', (g.user['id'],)).fetchone()
        teacher_id  = None
        if teacher:
            teacher_id = teacher['id']
        groups = db.execute('SELECT groups.id AS group_id, groups.title AS group_title, classes.id AS class_id from classes LEFT JOIN groups ON groups.id = classes.group_id WHERE classes.teacher_id = ?', (teacher_id,)).fetchall()
        classes = dict()
        for group in groups:
            classes[group['group_id']] = \
                    db.execute('SELECT classes.title AS title FROM classes WHERE classes.group_id = ? AND classes.teacher_id = ?', (teacher_id, group['group_id'])).fetchall()


    return render_template('/classes/classes.html', classes=classes, groups=groups)


