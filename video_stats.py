import requests
import json
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
api_key = os.getenv("api_key")

# channel_handle
channel_name = 'HaseebAli'

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

def extract_video_data(video_ids):

    video_data = []

    for video_id in video_ids:
        url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_id}&key={api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                video_info = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'viewCount': item['statistics'].get('viewCount', 0),
                    'likeCount': item['statistics'].get('likeCount', 0),
                    'commentCount': item['statistics'].get('commentCount', 0),
                    'duration': item['contentDetails']['duration']
                }
                video_data.append(video_info)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    return video_data


def save_to_json(extracted_data):
    
    file_path = f'./data/yt_data_{date.today()}.json'
    
    with open(file_path, 'w', encoding='utf=8') as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
