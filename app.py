import urllib.parse
import pyodbc
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, flash, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import load_only



params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=giftcricledbserver.database.windows.net;DATABASE=NightLifeConnect;UID=balunlu;PWD=Luq#123450;Connection Timeout=60")

conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.balance}')"
    
class Musician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    instrument = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Musician('{self.name}', '{self.instrument}')"


playlist_musician = db.Table('playlist_musician',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('musician_id', db.Integer, db.ForeignKey('musician.id'), primary_key=True)
)
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    cover_art = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('playlists', lazy=True))
    musicians = db.relationship('Musician', secondary=playlist_musician, backref=db.backref('playlists', lazy=True))
    share_cost = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"Playlist('{self.name}', '{self.description}', '{self.cover_art}', '{self.user.name}')"


class DJ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    accepted_playlists = db.relationship('Playlist', secondary='acceptances', backref=db.backref('djs', lazy=True))

    def __repr__(self):
        return f"DJ('{self.name}', '{self.email}', '{self.phone}')"
 
"""
class DJ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    playlists = db.relationship('Playlist', backref='dj', lazy=True)

    def __repr__(self):
        return f"DJ('{self.name}', '{self.email}')"
"""

acceptances = db.Table('acceptances',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('dj_id', db.Integer, db.ForeignKey('dj.id'), primary_key=True)
)


# create the database tables before the first request is processed
@app.before_first_request
def create_tables():
    # create any missing tables
    db.create_all()

    # check if any updates to the models have been made
    # and apply those updates to the database schema
    #with app.app_context():
    #    migration_dir = os.path.join(basedir, 'migrations')
    #    command.upgrade(migration_dir)

    # save any changes to the database
    #db.session.commit()

    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('You are now signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/dj_signup', methods=['GET', 'POST'])
def dj_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        dj = DJ(name=name, email=email, password=password)
        db.session.add(dj)
        db.session.commit()
        flash('DJ account created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('dj_signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('You are now logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

"""
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to view your dashboard', 'error')
        return redirect(url_for('login'))

    user = User.query.options(load_only(User.id, User.name, User.balance)).filter_by(id=session['user_id']).first()
    playlists = Playlist.query.options(load_only(Playlist.id, Playlist.name, Playlist.share_cost)).filter_by(user=user).all()
    djs = DJ.query.all()

    return render_template('dashboard.html', user=user, playlists=playlists, djs=djs)
"""

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard', 'error')
        return redirect(url_for('login'))

    user = User.query.options(load_only(User.id, User.name, User.email)).filter_by(id=session['user_id']).first()
    playlists = user.playlists

    return render_template('dashboard.html', user=user, playlists=playlists)

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if 'user_id' not in session:
        flash('Please log in to create a playlist', 'error')
        return redirect(url_for('login'))
    
    user = User.query.options(load_only(User.id)).filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        cover_art = request.form['cover_art'].strip()
        playlist = Playlist(name=name, description=description, cover_art=cover_art, user=user)
        db.session.add(playlist)

        musicians = []
        for musician in request.form.getlist('musicians'):
            musician_name, instrument = map(str.strip, musician.split(','))
            if musician_name and instrument:
                musicians.append(Musician(name=musician_name, instrument=instrument))
        playlist.musicians = musicians
        db.session.commit()

        flash('Playlist created successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_playlist.html', user=user)

#############################################################################
"""
@app.route('/share_playlist/<int:playlist_id>', methods=['POST'])
def share_playlist(playlist_id):
    if 'user_id' not in session:
        flash('Please log in to share a playlist', 'error')
        return redirect(url_for('login'))

    user = User.query.options(load_only(User.id)).filter_by(id=session['user_id']).first()
    playlist = Playlist.query.options(load_only(Playlist.id)).filter_by(id=playlist_id, user=user).first()

    if not playlist:
        flash('Playlist not found', 'error')
        return redirect(url_for('dashboard'))

    dj_id = request.form.get('dj_id')

    if not dj_id:
        flash('Please select a DJ to share the playlist with', 'error')
        return redirect(url_for('dashboard'))

    dj = DJ.query.get(dj_id)

    if not dj:
        flash('Selected DJ not found', 'error')
        return redirect(url_for('dashboard'))

    if user.balance < playlist.share_cost:
        flash('You do not have enough balance to share this playlist', 'error')
        return redirect(url_for('dashboard'))

    user.balance -= playlist.share_cost
    dj.balance += playlist.share_cost

    db.session.commit()

    flash(f'Playlist shared with {dj.name} successfully', 'success')
    return redirect(url_for('dashboard'))
"""

@app.route('/playlist/<int:playlist_id>/share', methods=['GET', 'POST'])
def share_playlist(playlist_id):
    if 'user_id' not in session:
        flash('Please log in to share a playlist', 'error')
        return redirect(url_for('login'))

    user = User.query.options(load_only(User.id, User.balance)).filter_by(id=session['user_id']).first()
    playlist = Playlist.query.options(load_only(Playlist.id, Playlist.share_cost, Playlist.musicians)).filter_by(id=playlist_id).first()

    if request.method == 'POST':
        dj_id = request.form['dj_id']
        dj = DJ.query.filter_by(id=dj_id).first()
        cost = playlist.share_cost + (playlist.share_cost * app.config['TRANSACTION_FEE'])
        if user.balance >= cost:
            user.balance -= cost
            for musician in playlist.musicians:
                dj.accepted_playlists.append(playlist)
            db.session.commit()
            flash('Playlist shared successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('You do not have enough funds to share this playlist', 'error')

    djs = DJ.query.all()
    return render_template('share_playlist.html', user=user, playlist=playlist, djs=djs)

if __name__ == '__main__':
   app.run(debug=True)
