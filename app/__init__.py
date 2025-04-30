from flask import Flask
from config import Config
from app.extensions import mysql, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.models import get_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    from app.routes import main
    app.register_blueprint(main)

    return app
