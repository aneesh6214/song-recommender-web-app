import os, secrets, openai
from dotenv import load_dotenv
from flask import Flask, render_template, request
from markupsafe import Markup
from routes.spotify import spotify_routes

# Load API key
load_dotenv()
openai.api_key = os.environ.get('API_KEY')

# Set up Flask application
app = Flask(__name__)
app.register_blueprint(spotify_routes, url_prefix='/spotify')
app.secret_key = secrets.token_urlsafe(16)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Route Handling
@app.route('/')
def index():
    return render_template('index.html')

# save previous results
results = []

@app.route('/submit', methods=['POST'])
def submit():
    song = request.form['song']
    prompt = (f"""Provide the name of a song that sounds similar to the given song, "{song},"\
              and belongs to a similar genre. Do not change the name
              of the original song in your output Format your response as follows: 
              
              [song - artist], [similar song - artist]

              For example:
              Input: Borderline by Tame Impala
              Output: Borderline - Tame Impala, Elephant - Tame Impala
        """)

    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=prompt,
        max_tokens=50
    )

    final_response = "<strong>Your Requested Song:</strong> " + \
        response["choices"][0]["text"].replace(
            ",", " <br><strong>Is Similar to:</strong>") + "<br>"

    results.insert(0, Markup(final_response))
    return render_template('index.html', results=results)


if __name__ == '__main__':
    results.clear()
    app.run()
