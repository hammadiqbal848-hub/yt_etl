import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")

# channel_handle
channel_name = 'VillageFoodSecrets'

url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_name}&key={api_key}'

def get_playlist_id():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        channel_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlist_id)
        return channel_playlist_id

    except requests.exceptions.RequestException as e:
        raise e
    
if __name__ == "__main__":
    get_playlist_id()

