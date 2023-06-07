import os, secrets, openai
from dotenv import load_dotenv
from flask import Flask, render_template, request
from markupsafe import Markup
from routes.spotify import spotify_routes, get_top_tracks

#setup environment variables
load_dotenv()
openai.api_key = os.environ.get('API_KEY')

#app config
app = Flask(__name__)
app.register_blueprint(spotify_routes, url_prefix='/spotify')
app.secret_key = secrets.token_urlsafe(16)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
results = []

# ==========================
# ===== ROUTE HANDLING =====
# ==========================
@app.route('/')
def index():
    """
    Renders the index.html template for the home page.
    """
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    #print(get_top_tracks())
    """
    Handles the form submission and generates a similar song recommendation based on the input song.

    Retrieves the input song from the form, creates a prompt for the OpenAI API,
    sends a request to the API to generate a completion, and formats the response.

    Returns the rendered index.html template with the results.
    """
    #retrieve form data
    song = request.form['song']

    #generate prompt
    messages=[
        {"role": "system", "content": "Your entire purpose is to help users find songs."},
        {"role": "user", "content": "Give a song that sounds similar to borderline by tame\
         impala. The song must be similar in sound and genre."},
        {"role": "assistant", "content": "Borderline - Tame Impala, Elephant - Tame Impala"},
        {"role": "user", "content": "That output format was perfect. Please keep future outputs\
         in the exact same format you used in your previous response: [original song - artist],\
         [similar song - artist]"},
        {"role": "system", "content": "I will keep the outputs in your requested format: \
         [original song - artist], [similar song - artist]"},
        {"role": "user", "content": f"Give me a song that sounds similar to {song}."}
    ]

    #query ai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    #format the response & insert into results list
    print(response)
    final_response = (
        "<strong>Your Requested Song:</strong> " +
        response["choices"][0]["message"]["content"].replace("\n", "").replace(",", " <br><strong>Is Similar to:</strong>") +
        "<br>"
    )
    print(final_response)
    results.insert(0, Markup(final_response))

    return render_template('index.html', results=results)

@app.route('/custom-recommendations')
def custom_recommendations():
    #get top tracks
    top_tracks = get_top_tracks()

    #generate prompt
    messages=[
        {"role": "system", "content": "Your entire purpose is to help users find songs."},

        {"role": "user", "content": "Give a song that sounds similar to borderline by tame\
         impala. The song must be similar in sound and genre. Do not add any unnecessary additional text.\
         Do not recommend me a song that I have already asked you about."},
         
        {"role": "assistant", "content": "Borderline - Tame Impala, Elephant - Tame Impala"},
        
        {"role": "user", "content": "That output format was perfect. Please keep future outputs\
         in the exact same format you used in your previous response: [original song - artist],\
         [similar song - artist]"},

        {"role": "system", "content": "I will keep the outputs in your requested format: \
         [original song - artist], [similar song - artist]"},

        {"role": "user", "content": f"Take a look at all of my top songs: ['teeth - brakence',\
         'hypochondriac - brakence', 'deepfake - brakence', 'Baby Blue - King Krule', 'Athoth a Go!! Go!! \
         - Machine Girl', 'intellectual greed - brakence', 'Echolalia - Yves Tumor', 'HELL/HEAVEN - keshi', \
         'The World to Come - Machine Girl', '5g - brakence', 'cbd - brakence', \
         'venus fly trap - brakence', 'Glass Ocean - Machine Girl', 'It Almost Worked - TV Girl', \
         'I've heard that song before - quinn', 'argyle - brakence', 'stung - brakence', 'goldfish - Jane Remover', \
         'and now a word from our sponsors - quinn']. Recommend me 10 songs that I would like based off of my top songs. \
         Output in an csv-like format similar to the input."},

        {"role": "assistant", "content": "Choke - I DONT KNOW HOW BUT THEY FOUND ME,Lost in Yesterday - Tame Impala,\
         Garden Song - Phoebe Bridgers,Pork Soda - Glass Animals,Alligator - Of Monsters and Men,Heavy - \
         Clever Girls,Genesis - Grimes,Daysleeper - R.E.M.,Warm Blood - Carly Rae Jepsen,Try Me - The Weeknd"},

        {"role": "user", "content": "That output was perfectly formatted. Please keep future outputs\
         in the exact same csv-like format you used in your previous response."},

        {"role": "system", "content": "I will keep the outputs in your requested csv-like format."},

        {"role": "user", "content": f"Take a look at all of my top songs: {top_tracks}. \
         Recommend me 10 songs that I would like based off of my top songs. \
         Output in a csv like format."},
    ]

    #query ai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.4,
        presence_penalty=0.7
    )

    # Get the top tracks
    print(response)
    response = response["choices"][0]["message"]["content"]
    response = list(response.split(","))
    print(response)
    
    # Render the custom recommendations template and pass the results
    return render_template('custom_recommendations.html', results=response)


if __name__ == '__main__':
    #reset data & start app
    results.clear()
    app.run()
