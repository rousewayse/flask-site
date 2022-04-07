import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

#g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request.
#current_app is another special object that points to the Flask application handling the request

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    schema = current_app.open_resource('database/schema.sql')
    db.executescript(schema.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('[DB] Database has been initialized')

#registring databases func with app

def init_app(app):
    #cleaning up
    app.teardown_appcontext(close_db)
    #new command for flusk like run
    app.cli.add_command(init_db_command)


