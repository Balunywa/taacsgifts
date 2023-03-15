from flask import Flask, render_template, flash, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, LoginManager, UserMixin
from models import User, DJ, Playlist, Song, Artist, Album, SearchResult, db
from forms import SearchForm, PlaylistForm, AddSongForm
from config import conn_str
from sqlalchemy.orm import load_only
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user




app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# Initialize the database
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
