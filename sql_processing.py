import json
import sqlite3

json_files = ['2024_top_songs.json', '2020_top_songs.json', '2016_top_songs.json', '2012_top_songs.json']

conn = sqlite3.connect('music_election.db')
cursor = conn.cursor()

# create music table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tracks (
    track_name TEXT,
    artists TEXT,
    genre TEXT,
    album TEXT,
    release_date TEXT,
    popularity INTEGER,
    year INTEGER
)
''')

# insert music data
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    for year, tracks in data.items():
        for track in tracks:
            track_name = track["track_name"]
            artists = ", ".join(track["artists"])
            genre = track["genre"]
            album = track["album"]
            release_date = track["release_date"]
            popularity = track["popularity"]
            
            cursor.execute('''INSERT INTO tracks (track_name, artists, genre, album, release_date, popularity, year) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                            (track_name, artists, genre, album, release_date, popularity, int(year)))

# create election table
cursor.execute('''
CREATE TABLE IF NOT EXISTS election_results (
    year INTEGER,
    party TEXT,
    presidential_nominee TEXT,
    vice_presidential_nominee TEXT,
    electoral_vote INTEGER,
    electoral_vote_percentage TEXT,
    popular_vote TEXT,
    popular_vote_percentage TEXT,
    winner TEXT
)
''')

# insert election data
with open('election_web_scrapping.json', 'r') as f:
    election_data = json.load(f)

for election in election_data:
    year = election["Year"]
    for data in election["Election Data"]:
        party = data["Party"]
        presidential_nominee = data["Presidential Nominee"]
        vice_presidential_nominee = data["Vice Presidential Nominee"]
        electoral_vote = int(data["Electoral Vote"])
        electoral_vote_percentage = data["Electoral Vote %"]
        popular_vote = data["Popular Vote"]
        popular_vote_percentage = data["Popular Vote %"]
        winner = data["Winner"]
        
        cursor.execute('''INSERT INTO election_results (year, party, presidential_nominee, vice_presidential_nominee,
                                      electoral_vote, electoral_vote_percentage, popular_vote, 
                                      popular_vote_percentage, winner) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                      (year, party, presidential_nominee, vice_presidential_nominee, electoral_vote, 
                                      electoral_vote_percentage, popular_vote, popular_vote_percentage, winner))

conn.commit()
conn.close()

print("Data from music and election JSON files has been inserted into SQLite.")
