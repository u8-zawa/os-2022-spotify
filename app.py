import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from utils import spotify

app = Flask(__name__, static_folder='./static')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


@app.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    scope = [
        'playlist-read-private',
        'user-top-read',
    ]
    auth_manager = SpotifyOAuth(client_id=spotify.CLIENT_ID,
                                client_secret=spotify.CLIENT_SECRET,
                                scope=scope,
                                cache_handler=cache_handler,
                                show_dialog=True)

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    sp = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('root.html', name=sp.me()['display_name'])


@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/my_playlists')
def my_playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = SpotifyOAuth(client_id=spotify.CLIENT_ID,
                                client_secret=spotify.CLIENT_SECRET,
                                cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    results = sp.current_user_playlists(limit=50)
    return render_template('my_playlists.html',
                           items=results['items'])


@app.route('/my_top_artists')
def my_top_artists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = SpotifyOAuth(client_id=spotify.CLIENT_ID,
                                client_secret=spotify.CLIENT_SECRET,
                                cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    ranges = ['short_term', 'medium_term', 'long_term']
    results = [sp.current_user_top_artists(time_range=sp_range, limit=50) for sp_range in ranges]
    i = request.args.get('term', default=0, type=int)
    return render_template('my_top_artists.html',
                           term=i,
                           items=results[i]['items'])


@app.route('/my_top_tracks')
def my_top_tracks():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = SpotifyOAuth(client_id=spotify.CLIENT_ID,
                                client_secret=spotify.CLIENT_SECRET,
                                cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    ranges = ['short_term', 'medium_term', 'long_term']
    results = [sp.current_user_top_tracks(time_range=sp_range, limit=50) for sp_range in ranges]
    i = request.args.get('term', default=0, type=int)
    return render_template('my_top_tracks.html',
                           term=i,
                           items=results[i]['items'])


if __name__ == '__main__':
    app.run(threaded=True, port=8080)
