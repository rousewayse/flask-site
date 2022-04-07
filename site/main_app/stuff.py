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
bp = Blueprint('stuff', __name__, url_prefix='/stuff')




def stuff_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        err = None

        user_id = g.user['id']
        db = get_db()
        
        ifStuff = db.execute(
            'SELECT * FROM stuff WHERE user_id = ?', (user_id,)
        ).fetchone()
        print(ifStuff) 
        err = None

        if ifStuff is None:
            err = "Stuff account required"
            flash(err)
            #return redirect( url_for('auth.login'))
            abort(403)
        return view(**kwargs)
    return wrapped_view


@bp.route('/', methods=['GET'])
@stuff_login_required
def stuff_main():
    db = get_db()

    users = db.execute("SELECT * FROM user").fetchall()
    students = db.execute("SELECT students.user_id AS user_id, groups.title AS group_title, user_info.fst_name AS fname, user_info.snd_name AS sname, user_info.thrd_name AS thname FROM students LEFT JOIN user_info ON user_info.user_id = students.user_id LEFT JOIN groups ON groups.id = students.group_id").fetchall()
    teachers  =db.execute('SELECT teachers.user_id AS user_id, faculty.title AS faculty_title, user_info.fst_name AS fname, user_info.snd_name AS sname, user_info.thrd_name AS thname FROM teachers LEFT JOIN user_info ON user_info.user_id = teachers.user_id LEFT JOIN faculty ON faculty.id = teachers.faculty_id').fetchall()
    faculties = db.execute("SELECT * FROM faculty").fetchall()
    groups = dict()
    classes = dict()
    for faculty in faculties:
        groups[faculty['id']] = db.execute("SELECT groups.id AS id, groups.title AS title, faculty.title AS faculty FROM groups LEFT JOIN faculty ON groups.faculty_id = faculty.id WHERE groups.faculty_id = ?", (faculty['id'],)).fetchall()
        for group in groups[faculty['id']]:
            group_id = group['id']
            classes[group_id] = db.execute("SELECT ? AS group_title, ? AS faculty_title, user_info.user_id AS teacher_id, classes.id AS id, classes.title AS title, user_info.fst_name AS teacher_fname, user_info.snd_name AS teacher_sname, user_info.thrd_name AS teacher_thname FROM classes LEFT JOIN teachers ON classes.teacher_id = teachers.id LEFT JOIN user_info ON user_info.user_id = teachers.user_id WHERE classes.group_id = ?", (group['title'], group['faculty'], group_id)).fetchall();   
            print([dict(c) for c in classes[group_id]], end='')
            print(group_id)
    return render_template('stuff/index.html', users=users, faculties=faculties, groups=groups, classes=classes, students=students, teachers=teachers)

@bp.route('/register', methods=['GET', 'POST'])
@stuff_login_required
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
        print(username)
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
                return redirect(url_for('stuff.stuff_user_info', username=username))
        flash(err)
    return render_template('stuff/register.html')

@bp.route('/user_info/<string:username>/', methods=['GET', 'POST'])
@stuff_login_required
def stuff_user_info(username = None):
    db = get_db()

    user = db.execute(
        'SELECT * FROM user WHERE username  = ?', (username, ) 
    ).fetchone()
    if user is None:
        abort(404)
    user_id = user['id']

    user_info = db.execute(
        'SELECT * FROM user_info WHERE user_id = ?', (user_id, )
    ).fetchone()
   
    g.user_info_to_update = user_info

    if request.method == 'POST':
        fst_name = request.form['fst_name']
        snd_name = request.form['snd_name']
        thrd_name = request.form['thrd_name']
        birth_date = request.form['birth_date']
        email = request.form['email']
        try:
            if user_info is None:
                db.execute(
                    'INSERT INTO user_info (user_id ,fst_name, snd_name, thrd_name, birth_date, email) VALUES (?, ?, ?, ?, ?, ?)', 
                    (user_id, fst_name, snd_name, thrd_name, birth_date, email,)
                )
            else:
                db.execute(
                    'UPDATE user_info SET fst_name = ?, snd_name = ?, thrd_name = ?, birth_date = ?, email = ? WHERE user_id = ?',
                    (fst_name, snd_name, thrd_name, birth_date, email, user_id,)
                )
            db.commit()
        except db.IntegrityError:
            flash("Operation failed")
            return render_template('stuff/user_info.html')        
        return redirect(url_for( 'stuff.stuff_main' ))
    return render_template('stuff/user_info.html')

@bp.route('/faculty/<int:id>/', methods=['GET', 'POST'])
@stuff_login_required
def faculty_info(id = None):
    db = get_db()

    faculty = db.execute('SELECT * FROM faculty WHERE id = ?', (id,)).fetchone()

    if faculty is None:
        abort(404)

    g.faculty_to_update = dict(faculty)

    if request.method == 'POST':
        faculty_title = request.form['title']
        try:
            db.execute('UPDATE faculty SET title = ? WHERE id = ?', (faculty_title, id, ))
            db.commit()
        except db.IntegrityError:
            flash ("Operation failed")
            return render_template('stuff/faculty_info.html')
        g.faculty_to_update['title'] = faculty_title
        return redirect( url_for('stuff.stuff_main'))
    return render_template('stuff/faculty_info.html')


@bp.route('/faculty/create', methods=['GET', 'POST'])
@stuff_login_required
def create_faculty():
    db = get_db()

    if request.method == 'POST':
        title = request.form['title']

        try:
            db.execute('INSERT INTO faculty (title) VALUES (?)', (title,))
            db.commit()
        except db.IntegrityError:
            flash("Operation failed")
        return redirect( url_for('stuff.stuff_main')) 
    return render_template('stuff/faculty_create.html')

def get_faculties(db):
    faculties = db.execute('SELECT *  FROM faculty').fetchall()
    if faculties is None:
        return None

    return [ dict(faculty) for faculty in faculties]
        

@bp.route('groups/create', methods=['GET', 'POST'])
@stuff_login_required
def group_create():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        faculty_title = request.form['faculty']

        faculty = db.execute('SELECT * FROM faculty WHERE title=?', (faculty_title,)).fetchone()
        if faculty is None:
            flash("NO SUCH FACULTY")
        faculty_id = faculty['id']
        try:
            db.execute('INSERT INTO groups (title, faculty_id) VALUES (?, ?)', (title, faculty_id,))
            db.commit()
        except db.IntegrityError:
            flash("Operation failed")
            return render_template('stuff/group_create.html', faculties=get_faculties(db))
        return redirect(url_for('stuff.stuff_main'))
       # return render_template('stuff/group_create.html')
    return render_template('stuff/group_create.html', faculties=get_faculties(db))

@bp.route('groups/info/<int:id>', methods=['GET', 'POST'])
@stuff_login_required
def group_info(id = None):
    
    if id is None:
        abort(404)

    db = get_db()
    group = db.execute('SELECT * FROM groups WHERE id = ?', (id,)).fetchone()
    if group is None:
        abort(404)
    group = dict(group)

    if request.method == 'POST':
        title = request.form['title']
        faculty_id = request.form['faculty_id']
        try:
            db.execute('UPDATE groups SET faculty_id = ?, title = ?  WHERE id = ?', (faculty_id, title, id))
            db.commit()
        except db.IntegrityError:
            flash("Operation failed")
            return render_template('stuff/group_info.html', faculties=get_faculties(), group_id = id, group=group)
        group['faculty_id'] = faculty_id
        group['title'] = title
        return redirect(url_for('stuff.stuff_main'))
        #return render_template('stuff/group_info.html', faculties=get_faculties(), group=group)
    return render_template('stuff/group_info.html', faculties=get_faculties(db), group_id = id, group = group)


def get_users(db):
    #LOOK AT THIS QUERY
    users = db.execute('SELECT user_info.fst_name AS fst_name, user_info.snd_name AS snd_name, user_info.thrd_name AS thrd_name, user_info.user_id AS user_id  from user_info LEFT JOIN user ON user.id = user_id WHERE user_id NOT IN (SELECT user_id FROM students UNION SELECT user_id FROM teachers UNION SELECT user_id from stuff) AND user.active=True').fetchall()
    if users is not None:
        return  [dict(user) for user in users]
    return None

def get_groups(db):
    groups = db.execute('select groups.id AS id, groups.title AS title, faculty.title AS faculty_title from groups LEFT JOIN faculty ON groups.faculty_id=faculty.id  ORDER BY faculty_title ASC;').fetchall()
    if groups is not None:
        return  [dict(group) for group in groups]
    return None

@bp.route('students/create', methods=['GET', 'POST'])
@stuff_login_required
def create_student():
    db = get_db()
    
    users = get_users(db)
    groups = get_groups(db)
    
    if request.method == 'POST':
        student_data = (
             request.form['user_id'],
             request.form['group_id'],
             request.form['cource'],
             request.form['directory'],
             request.form['degree'],
             request.form['form'],
             request.form['fee']
        )

        try:
            db.execute(
                'INSERT INTO students (user_id, group_id, cource, directory, degree, form, fee) VALUES (?, ?, ?, ?, ?, ?, ?)', student_data
                    )
            db.commit()
            
        except db.IntegrityError:
            flash("Operation failed")
            return redirect( url_for('stuff.create_student'))
    return render_template('stuff/student_create.html', groups=groups, users=users)


@bp.route('students/info/<int:id>', methods=['GET', 'POST'])
@stuff_login_required
def student_info(id = None):
    if id is None:
        abort(404)

    db = get_db()
    
    student = db.execute('SELECT * FROM students WHERE user_id = ?', (id,)).fetchone()
    if student is None:
        abort(404)

    student = dict(student)
    groups = get_groups(db)
    
    if request.method == 'POST':
        student_data = (
             request.form['group_id'],
             request.form['cource'],
             request.form['directory'],
             request.form['degree'],
             request.form['form'],
             request.form['fee'],
             id
        )

        try:
            db.execute(
                'UPDATE students SET  group_id = ?, cource = ?, directory = ?,  degree = ?, form = ?, fee = ? WHERE user_id = ? ', student_data
                    )
            db.commit()
            student = db.execute('SELECT * FROM students WHERE user_id = ?', (id,)).fetchone()
        except db.IntegrityError:
            flash("Operation failed")
            return redirect( url_for('stuff.student_info'))

    return render_template('stuff/student_info.html', groups=groups, student=student)


@bp.route('teachers/create', methods = ['GET', 'POST'])
@stuff_login_required
def create_teacher():
    db = get_db()
    faculties = get_faculties(db);
    users = get_users(db)
    if request.method == 'POST':
        teacher_data = (
                request.form['user_id'],
                request.form['degree'],
                request.form['faculty_id']
        )

        try: 
            db.execute(
                'INSERT INTO teachers (user_id, degree, faculty_id) VALUES (?, ?, ?)', teacher_data
            )
            db.commit()
        except db.IntegrityError:
            flash("Operation failed")
            return redirect( url_for('stuff.create_teacher')  )
        return redirect(url_for('stuff.stuff_main'))
    return render_template('stuff/teacher_create.html', faculties=faculties, users=users)

@bp.route('teachers/info/<int:id>', methods=['GET', 'POST'])
@stuff_login_required
def teacher_info(id = None):
    if id is None:
        abort(404)
    db = get_db()
    teacher =  db.execute('SELECT * FROM teachers WHERE user_id = ?', (id,)).fetchone()
    if teacher is None:
        abort(404)
    
    teacher = dict(teacher)
    if request.method == 'POST':
        teacher_data = (
                request.form['faculty_id'],
                request.form['degree'],
                id
        )
        try:
            db.execute('UPDATE teachers SET faculty_id = ?, degree = ? WHERE user_id = ?', teacher_data)
            db.commit()
        except db.IntegrityError:
            flash('Operation failed')
            reditect( url_for('stuff.teacher_info'), id = id )
        teacher = db.execute('SELECT * FROM teachers WHERE user_id = ?', (id,)).fetchone()
        return redirect(url_for('stuff.stuff_main'))
    return render_template('stuff/teacher_info.html', teacher=teacher, faculties=get_faculties(db))

def get_teachers(db):
    teachers = db.execute('SELECT * FROM teachers').fetchall()
    if teachers is not None:
       return  [dict(teacher) for teacher in teachers]
    return None
        

@bp.route('classes/create', methods=['GET', 'POST'])
@stuff_login_required
def create_class():
    db = get_db()
    
    groups = get_groups(db)
    teachers = db.execute('select teachers.id AS id, faculty.title AS faculty, user_info.fst_name AS fst_name, user_info.snd_name AS snd_name, user_info.thrd_name AS thrd_name FROM teachers LEFT JOIN faculty ON teachers.faculty_id = faculty.id LEFT JOIN user_info ON teachers.user_id = user_info.user_id').fetchall()
    if teachers is not None:
        teachers = [dict(t) for t in teachers]

    if request.method == 'POST':
        class_data = (
                request.form['group_id'],
                request.form['teacher_id'],
                request.form['title']
        )

        try:
            db.execute('INSERT INTO classes (group_id, teacher_id, title) VALUES (?, ?, ?)', class_data)
            db.commit();
        except db.IntegrityError:
            flash('Operation failed')
            redirect( url_for('stuff.create_class') )
        return redirect(url_for('stuff.stuff_main'))
    return render_template('stuff/class_create.html', teachers=teachers, groups=groups)

@bp.route('classes/info/<int:id>', methods=['GET', 'POST'])
@stuff_login_required
def class_info(id = None):
    if id is None:
        abort(404)
    db = get_db()
    
    groups = get_groups(db)
    teachers = db.execute('select teachers.id AS id, faculty.title AS faculty, user_info.fst_name AS fst_name, user_info.snd_name AS snd_name, user_info.thrd_name AS thrd_name FROM teachers LEFT JOIN faculty ON teachers.faculty_id = faculty.id LEFT JOIN user_info ON teachers.user_id = user_info.user_id').fetchall()
    if teachers is not None:
        teachers = [dict(t) for t in teachers]
    class_ = db.execute('SELECT * FROM classes WHERE id = ?', (id,)).fetchone()
    if class_ is None:
        abort(404)
    class_ = dict(class_)

    if request.method == 'POST':
        class_data = (
                request.form['teacher_id'],
                request.form['title'],
                id
        )

        try:
            db.execute('UPDATE classes SET teacher_id = ? , title = ? WHERE id = ?', class_data)
            db.commit();
        except db.IntegrityError:
            flash('Operation failed')
            redirect( url_for('stuff.class_info'), id = id )
        class_ = db.execute('SELECT * FROM classes WHERE id = ?', (id,)).fetchone()
    return render_template('stuff/class_info.html',class_=class_,  teachers=teachers, groups=groups)


