from flask import Flask
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

# Initialize Extensions
mongo = MongoClient(Config.MONGO_URI)
db = mongo.get_database("PlacementDB")
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from core.routes import main
    app.register_blueprint(main)

    return app