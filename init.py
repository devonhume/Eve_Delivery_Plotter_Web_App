from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap4
from flask_modals import Modal
from flask_login import LoginManager

# Create Flask App
app = Flask(__name__)

# Configure QLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plotter_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set Secret Keys
app.config['SECRET_KEY'] = 'PandasEatBamboo'
app.config['WTF_CSRF_SECRET_KEY'] = 'PandasEatAllTheBamboo'

# Create Database, Bootstrap, Modal, and Login objects
db = SQLAlchemy(app)
bootstrap = Bootstrap4(app)
modal = Modal(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'


