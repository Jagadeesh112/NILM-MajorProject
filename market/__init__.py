from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ocbmivptovdxou:09bc7f2c554c8eedd46fd3dc154f3a875b17fb4ad29b8a17b01711b10c8376e5@ec2-3-217-113-25.compute-1.amazonaws.com:5432/d57v8hpoh477kg'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
from market import routes