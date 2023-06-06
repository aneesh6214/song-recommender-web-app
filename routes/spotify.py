import spotipy, secrets, os, time
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, url_for, session, request, redirect
import pandas as pd

load_dotenv()
env_client_id = os.environ.get('CLIENT_ID')
env_client_secret = os.environ.get('CLIENT_SECRET')

# App config
spotify_routes = Blueprint('spotify', __name__)
spotify_routes.secret_key = secrets.token_urlsafe(16)
spotify_routes.config = {
    'SESSION_COOKIE_NAME': 'spotify-login-session'}

@spotify_routes.route('/login')
def login():
    """
    Initiates the Spotify login flow.

    Redirects the user to the Spotify authorization page.
    """
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@spotify_routes.route('/redirect')
def redirect_page():
    """
    Handles the redirect from the Spotify authorization page.

    Retrieves the access code from the redirect URL, exchanges it for an access token,
    and stores the token information in the session.
    """
    sp_oauth = create_spotify_oauth()
    session.clear()
    
    access_code = request.args.get('code')
    token_info = sp_oauth.get_access_token(access_code)
    session["token_info"] = token_info
    return redirect(url_for("spotify.get_all_tracks", _external=True))


@spotify_routes.route('/getTracks')
def get_all_tracks():
    token = get_token()
    session['token_info'] = token
    authorized = token
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    
    #df = pd.DataFrame(results, columns=["song names"]) 
    #df.to_csv('songs.csv', index=False)
    print(results)
    return results

def get_token():
    token_info = session.get("token_info", None)
    if not token_info:
        raise "Exception: Not Logged In"
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

@spotify_routes.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=env_client_id,
        client_secret=env_client_secret,
        redirect_uri=url_for('spotify.redirect_page', _external=True),
        scope="user-library-read"
    )
