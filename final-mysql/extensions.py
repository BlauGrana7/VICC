from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap4()