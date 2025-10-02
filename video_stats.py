import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")

# channel_handle
channel_name = 'VillageFoodSecrets'

def get_playlist_id():

    url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_name}&key={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        channel_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlist_id)
        return channel_playlist_id

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    
def get_video_ids(playlist_id):

    video_ids = []
    max_results = 50
    pageToken = ''

    while True:
        url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&key={api_key}&maxResults={max_results}'
        if pageToken:
            url += f'&pageToken={pageToken}'
        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_ids.append(item['contentDetails']['videoId'])

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    return video_ids


if __name__ == "__main__":
    playlist_id = get_playlist_id()
    print(get_video_ids(playlist_id))
