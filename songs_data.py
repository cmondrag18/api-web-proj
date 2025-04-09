import requests
import json


def get_json_content(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
        return json_dict

ttwelve_list = []
file_twelve = "2012_top_songs.json"
ttwelve_data = get_json_content(file_twelve)

if ttwelve_data: 
    ttwelve_songs = ttwelve_data.get("2012", [])
    for song in ttwelve_songs:
        track_name = song.get('track_name')
        if track_name:
            ttwelve_list.append(track_name)

print(ttwelve_list)


