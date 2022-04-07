import os

from flask import Flask, render_template

def create_app ():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "dev"
    app.config.from_mapping(
            #Used for keeping data app safe
            SECTRET_KEY='dev',
            #path for database file
            DATABASE = os.path.join(app.instance_path, 'database.sqlite')
            )
    app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/test')
    def test():
        return "This is test page"
    
    from . import database as db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import stuff
    app.register_blueprint(stuff.bp)
    
    from . import profile
    app.register_blueprint(profile.bp)
    
    from . import classes
    app.register_blueprint(classes.bp)

    @app.route('/') 
    @app.route('/index')
    def index():
        return render_template('index.html')
    

    return app


