import json
import sqlite3
from datetime import datetime
import pandas as pd


json_files = ['2024_top_songs.json', '2020_top_songs.json', '2016_top_songs.json', '2012_top_songs.json']


conn = sqlite3.connect('sql_processing_final.db')
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


# clear existing data to avoid duplicates in tracks table
cursor.execute("DELETE FROM tracks")


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


# clear existing data to avoid duplicates in election_results table
cursor.execute("DELETE FROM election_results")


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


# MIA'S CODE

# === Create movie_genre_id table (normalized genres) ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_genre_id (
   id INTEGER PRIMARY KEY,
   genre TEXT UNIQUE
)
''')

# === Create box_office_movies table if it doesn't already exist ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS box_office_movies (
   genre_id INTEGER,
   year INTEGER,
   title TEXT,
   revenue INTEGER,
   FOREIGN KEY (genre_id) REFERENCES movie_genre_id(id)
)
''')

# === Insert up to 25 NEW movies from cache_tmdb.json ===
with open('cache_tmdb.json', 'r') as f:
   movie_data = json.load(f)

insert_count = 0
for key, movie in movie_data.items():
    if insert_count >= 25:
        break

    if movie:
        genre, year = key.rsplit("-", 1)
        title = movie.get("title", "")
        revenue = movie.get("revenue", 0)

        # Skip if this movie is already in the table
        cursor.execute("SELECT 1 FROM box_office_movies WHERE title = ? AND year = ?", (title, int(year)))
        if cursor.fetchone():
            continue

        # Insert genre if it doesn't exist
        cursor.execute("INSERT OR IGNORE INTO movie_genre_id (genre) VALUES (?)", (genre,))
        cursor.execute("SELECT id FROM movie_genre_id WHERE genre = ?", (genre,))
        genre_id = cursor.fetchone()[0]

        # Insert movie with genre_id
        cursor.execute('''
            INSERT INTO box_office_movies (genre_id, year, title, revenue)
            VALUES (?, ?, ?, ?)
        ''', (genre_id, int(year), title, revenue))

        insert_count += 1

print(f"{insert_count} new movies inserted into box_office_movies.")



# insert data from top_20_movies_by_year.json


# with open('top_20_movies_by_year.json', 'r') as f:
#     top_movies = json.load(f)


# for year, movies in top_movies.items():
#     for movie in movies:
#         title = movie.get("title", "")
#         genre = movie.get("genre", "")
#         revenue = movie.get("revenue", 0)
#         cursor.execute('''
#             INSERT INTO top_grossing_movies (year, title, genre, revenue)
#             VALUES (?, ?, ?, ?)
#         ''', (int(year), title, genre, revenue))


# END OF MIA CODE


#created separate music_genres table to hold music genres and an integer value
cursor.execute('''
CREATE TABLE IF NOT EXISTS music_genres (
   genre_id INTEGER PRIMARY KEY,
   genre_name TEXT UNIQUE
)
''')


genres = set()  # To store unique genres from music data
for json_file in json_files:
   with open(json_file, 'r') as f:
       data = json.load(f)
  
   for year, tracks in data.items():
       for track in tracks:
           genres.add(track["genre"])


for genre in genres:
   cursor.execute("INSERT OR IGNORE INTO music_genres (genre_name) VALUES (?)", (genre,))


# Create the 'music_election' table: outer join between 'tracks' and 'election_results' on 'year'
cursor.execute("DROP TABLE IF EXISTS music_election")  # drop if already exists
cursor.execute('''
CREATE TABLE music_election AS
SELECT
   t.year,
   t.track_name AS title,
   g.genre_id,  -- Use genre_id from music_genres table
   t.popularity AS popularity,
   e.party,
   e.presidential_nominee,
   e.vice_presidential_nominee,
   e.electoral_vote,
   e.electoral_vote_percentage,
   e.popular_vote,
   e.popular_vote_percentage,
   e.winner,
   t.release_date  -- Explicitly include release_date here
FROM tracks t
LEFT OUTER JOIN election_results e ON t.year = e.year
LEFT OUTER JOIN music_genres g ON t.genre = g.genre_name
GROUP BY t.year, t.track_name  -- Group by year and track_name to remove duplicates
ORDER BY t.year;
''')


# create the 'movie_election' table: join box_office_movies, movie_genre_id, and election_results
# === Create movie_election JOIN table (uses genre_id directly) ===
cursor.execute("DROP TABLE IF EXISTS movie_election")
cursor.execute('''
CREATE TABLE movie_election AS
SELECT
   b.year,
   b.title,
   b.genre_id,
   b.revenue,
   e.party,
   e.presidential_nominee,
   e.vice_presidential_nominee,
   e.electoral_vote,
   e.electoral_vote_percentage,
   e.popular_vote,
   e.popular_vote_percentage,
   e.winner
FROM box_office_movies b
LEFT OUTER JOIN election_results e ON b.year = e.year
ORDER BY b.year;
''')


# select release date and year from tracks table
query = '''
SELECT release_date, year
FROM tracks
'''


df = pd.read_sql_query(query, conn)


# release_date is in datetime format (YYYY-MM-DD), extract the month and year
df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d', errors='coerce')
df['month'] = df['release_date'].dt.month
df['year'] = df['year'].astype(int)


# count the occurrences of songs by year and month
song_counts = df.groupby(['year', 'month']).size().reset_index(name='song_count')
output_file_path = 'song_counts_by_month_and_year.txt'  # Update with your desired path
with open(output_file_path, 'w') as f:
   for index, row in song_counts.iterrows():
       f.write(f"Year: {row['year']}, Month: {row['month']}, Song Count: {row['song_count']}\n")




conn.commit()
conn.close()


print("Data has been successfully gathered and processed")
