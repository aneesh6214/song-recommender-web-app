import openai
import os
from dotenv import load_dotenv

# load api key
load_dotenv()
openai.api_key = os.environ.get('API_KEY')

song = input("Pick a song: ")
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
    max_tokens=50)

print(response)
print(response["choices"][0]["text"])
