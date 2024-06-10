from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
db_name="mydb"


def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY'] = "123ovidiu345"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ovidiu@db:3306/mydb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    #  pozele se salveaza aici (PERMISIUNII) dar eu in update.py sunt in website/update.py !! daca schimb
    UPLOAD_FOLDER=r'C:/Users/calit/Licenta - Copy/venv/website/static/profile_photo'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

    auto_update_db = Migrate(app, db)


    from views import views
    from auth import auth
    from update import updatedd
    from friends import friends
    from notificare import notificare
    from games import games
    from events import events
    from recenzie import recenzie

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(updatedd,url_prefix='/')
    app.register_blueprint(friends,url_prefix='/')
    app.register_blueprint(notificare,url_prefix='/')
    app.register_blueprint(games,url_prefix='/')
    app.register_blueprint(events,url_prefix='/')
    app.register_blueprint(recenzie,url_prefix='/')

    from models import Utilizator,Mesaje_chat,Friendship,Postare,Comentariu,Joc,Biblioteca_joc,Recenzie,Eveniment,Participare_eveniment


    with app.app_context():
       db.create_all()

    login_manager=LoginManager()
   #unde trebuie sa fim daca nu suntem logati
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

   #cum dam load la user cu ajutorul PK
    @login_manager.user_loader
    def load_user(id_utilizator):
      return Utilizator.query.get(int(id_utilizator))

    return app

