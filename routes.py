from flask import render_template, flash, redirect, url_for, session, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, DJ, Playlist, Song, Artist, Album, SearchResult
from forms import SearchForm, PlaylistForm, AddSongForm
import requests
from sqlalchemy.orm import load_only
from flask_login import login_user, logout_user
import json
from sqlalchemy.orm import joinedload



@app.before_first_request
def create_tables():
    db.create_all()

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
            login_user(user)  # Use Flask-Login's login_user function
            flash('You are now logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    playlists = Playlist.query.options(joinedload(Playlist.songs)).filter_by(user_id=user_id).all()
    return render_template('dashboard.html', playlists=playlists)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    user_id = current_user.id
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search_term.data
        url = f"https://itunes.apple.com/search?term={search_term}&entity=musicTrack"
        response = requests.get(url)
        if response.ok:
            data = response.json()['results']
            user_id = current_user.id if current_user.is_authenticated else None
            return render_template('search_results.html', data=data, search_term=search_term, user_id=user_id)
        else:
            flash('Error: could not connect to iTunes API', 'error')
    return render_template('search.html', form=form)


@app.route('/add_song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def add_song(song_id):
    user_id = current_user.id
   
    song = Song.query.get(song_id)

    form = AddSongForm()
    if form.validate_on_submit():
        playlist_id = form.playlist_id.data
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
        if playlist:
            playlist.songs.append(song)
            db.session.commit()
            flash('Song added to playlist successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('You do not have permission to modify this playlist', 'error')

    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return render_template('add_song.html', song=song, playlists=playlists, form=form)


@app.route('/create_playlist', methods=['POST'])
@login_required
def create_playlist():
    user_id = current_user.get_id()
    selected_songs = request.form.getlist('selected_songs')
    
    for song_data in selected_songs:
        song = json.loads(song_data)
        
        # Add the print statement to output the song data to the console
        print(song)
        
        new_song = Song(
            user_id=user_id,
            track_id=song['trackId'],
            track_name=song['trackName'],
            artist_name=song['artistName'],
            album_name=song['collectionName'],
            preview_url=song['previewUrl'],
            artwork_url=song['artworkUrl100']
        )
        
        db.session.add(new_song)
    
    db.session.commit()
    flash('Playlist created successfully!', 'success')
    return redirect(url_for('dashboard'))







    # Rest of the code related to the create_playlist function

@app.route('/playlist/<int:playlist_id>')
@login_required
def playlist(playlist_id):
    user_id = current_user.id
    
    if 'user_id' not in session:
        flash('Please log in to view your playlist', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.options(load_only(User.id, User.name, User.email)).filter_by(id=user_id).first()
    playlist = Playlist.query.options(joinedload(Playlist.songs).joinedload(Song.artist).joinedload(Artist.albums)).filter_by(id=playlist_id).first()

    return render_template('playlist.html', user=user, playlist=playlist)


@app.route('/share_playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def share_playlist(playlist_id):
    user_id = current_user.id
    

    user_id = session['user_id']
    user = User.query.get(user_id)
    playlist = Playlist.query.get(playlist_id)

    if playlist.user_id != user_id:
        flash('You do not have permission to share this playlist', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.filter(User.id != user_id).all()

    if request.method == 'POST':
        selected_users = request.form.getlist('users')

        for user_id in selected_users:
            share = Share(user_id=user_id, playlist_id=playlist.id)
            db.session.add(share)

        db.session.commit()
        flash('Playlist shared successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('share_playlist.html', user=user, playlist=playlist, users=users)

   

