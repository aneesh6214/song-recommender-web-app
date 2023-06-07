import openai, os
from dotenv import load_dotenv

# load api key
load_dotenv()
openai.api_key = os.environ.get('API_KEY')

song = input("Pick a song: ")
messages=[
        {"role": "system", "content": "Your entire purpose is to help users find songs."},
        {"role": "user", "content": "Give a song that sounds similar to borderline by tame\
         impala. The song must be similar in sound and genre."},
        {"role": "assistant", "content": "Borderline - Tame Impala, Elephant - Tame Impala"},
        {"role": "user", "content": "That ouput format was perfect. Please keep future outputs\
         in the exact same format you used in your previous response: [original song - artist],\
         [similar song - artist]"},
        {"role": "system", "content": "I will keep the outputs in your requested format: \
         [original song - artist], [similar song - artist]"},
        {"role": "user", "content": f"Give me a song that sounds similar to {song}."}
    ]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

print(response)
print(response["choices"][0]["message"]["content"])

