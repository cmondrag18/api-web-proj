import json
import sqlite3
from datetime import datetime
import pandas as pd


json_files = ['2024_top_songs.json', '2020_top_songs.json', '2016_top_songs.json', '2012_top_songs.json']


conn = sqlite3.connect('sql_processing_take2.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS music_genres (
   genre_id INTEGER PRIMARY KEY,
   genre_name TEXT UNIQUE
)
''')

# Collect all unique genres from the JSON files
genres = set()
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)

    for year, tracks in data.items():
        for track in tracks:
            genres.add(track["genre"])

# Convert the set to a list for easier processing
genres_list = list(genres)

# Set the counter and the batch size (25 genres at a time)
counter = 0
batch_size = 25

# Insert genres into the music_genres table, up to 25 genres
for genre in genres_list:
    if counter >= batch_size:
        break  # Stop once 25 genres have been inserted
    cursor.execute("INSERT OR IGNORE INTO music_genres (genre_name) VALUES (?)", (genre,))
    counter += 1

# Commit the transaction to the database
conn.commit()

# Optionally, print how many genres were inserted
print(f"Inserted {counter} genres.")


cursor.execute('''
CREATE TABLE IF NOT EXISTS tracks (
   track_name TEXT,
   genre_id INTEGER,
   release_date TEXT,
   popularity INTEGER,
   year INTEGER,
   FOREIGN KEY (genre_id) REFERENCES music_genres(genre_id)
)
''')

# Find the number of records already inserted
cursor.execute("SELECT COUNT(*) FROM tracks")
existing_records = cursor.fetchone()[0]

insert_count = 0
processed_count = 0  # Keeps track of records processed from the JSON file

# Open JSON files for top songs of each year
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)

    for year, tracks in data.items():
        for track in tracks:
            if insert_count >= 25:
                break  # Stops at 25

            # Ensure that duplicate tracks are not re-added
            cursor.execute("SELECT 1 FROM tracks WHERE track_name = ? AND year = ?", (track["track_name"], int(year)))
            if cursor.fetchone():  # Skips track that already exists
                continue

            # Get the genre_id from the music_genres table based on the genre name
            cursor.execute("SELECT genre_id FROM music_genres WHERE genre_name = ?", (track["genre"],))
            genre_id = cursor.fetchone()

            if genre_id:
                genre_id = genre_id[0]
            else:
                genre_id = None  # In case the genre is not found

            # Insert new records that haven't been inserted yet
            track_name = track["track_name"]
            release_date = track["release_date"]
            popularity = track["popularity"]

            cursor.execute('''INSERT INTO tracks (track_name, genre_id, release_date, popularity, year)
                            VALUES (?, ?, ?, ?, ?)''',
                            (track_name, genre_id, release_date, popularity, int(year)))

            insert_count += 1  # Increment insert_count after each insertion
            processed_count += 1  # Count the number of processed records

        if insert_count >= 25:
            break  # Stop processing further data after 25 records
    if insert_count >= 25:
        break  # Stop processing files once 25 records have been inserted
cursor.execute('''
CREATE TABLE IF NOT EXISTS parties (
   party_id INTEGER PRIMARY KEY AUTOINCREMENT,
   party_name TEXT UNIQUE NOT NULL
)
''')

# Create the candidates table with candidate name and party_id reference
cursor.execute('''
CREATE TABLE IF NOT EXISTS candidates (
   candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
   candidate_name TEXT NOT NULL,
   party_id INTEGER,
   FOREIGN KEY (party_id) REFERENCES parties(party_id)
)
''')

# Create the election_results table
# cursor.execute("DROP TABLE IF EXISTS election_results")

# Recreate the election_results table with the updated schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS election_results (
   year INTEGER,
   party_id INTEGER,
   presidential_nominee_id INTEGER,
   vice_presidential_nominee_id INTEGER,
   electoral_vote INTEGER,
   electoral_vote_percentage TEXT,
   popular_vote TEXT,
   popular_vote_percentage TEXT,
   winner TEXT,
   FOREIGN KEY (party_id) REFERENCES parties(party_id),
   FOREIGN KEY (presidential_nominee_id) REFERENCES candidates(candidate_id),
   FOREIGN KEY (vice_presidential_nominee_id) REFERENCES candidates(candidate_id)
)
''')

# clear existing data to avoid duplicates in election_results table
cursor.execute("DELETE FROM election_results")
cursor.execute("DELETE FROM candidates")
cursor.execute("DELETE FROM parties")

parties = {}
candidates = {}

# Insert parties and candidates into the tables
with open('election_web_scrapping.json', 'r') as f:
    election_data = json.load(f)

for election in election_data:
    year = election["Year"]
    for data in election["Election Data"]:
        party_name = data["Party"]
        presidential_nominee = data["Presidential Nominee"]
        vice_presidential_nominee = data["Vice Presidential Nominee"]
        
        # Insert party if not already in parties table
        if party_name not in parties:
            cursor.execute('''INSERT INTO parties (party_name) VALUES (?)''', (party_name,))
            parties[party_name] = cursor.lastrowid  # Get the last inserted ID for the party
        
        party_id = parties[party_name]

        # Insert presidential nominee if not already in candidates table
        if presidential_nominee not in candidates:
            cursor.execute('''INSERT INTO candidates (candidate_name, party_id) VALUES (?, ?)''', 
                           (presidential_nominee, party_id))
            candidates[presidential_nominee] = cursor.lastrowid  # Get the last inserted ID for the candidate

        # Insert vice-presidential nominee if not already in candidates table
        if vice_presidential_nominee not in candidates:
            cursor.execute('''INSERT INTO candidates (candidate_name, party_id) VALUES (?, ?)''', 
                           (vice_presidential_nominee, party_id))
            candidates[vice_presidential_nominee] = cursor.lastrowid  # Get the last inserted ID for the candidate

        presidential_nominee_id = candidates[presidential_nominee]
        vice_presidential_nominee_id = candidates[vice_presidential_nominee]

        electoral_vote = int(data["Electoral Vote"])
        electoral_vote_percentage = data["Electoral Vote %"]
        popular_vote = data["Popular Vote"]
        popular_vote_percentage = data["Popular Vote %"]
        winner = data["Winner"]

        # Insert election result using foreign keys
        cursor.execute('''INSERT INTO election_results (year, party_id, presidential_nominee_id, vice_presidential_nominee_id,
                                        electoral_vote, electoral_vote_percentage, popular_vote, popular_vote_percentage, winner) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                        (year, party_id, presidential_nominee_id, vice_presidential_nominee_id, electoral_vote,
                                        electoral_vote_percentage, popular_vote, popular_vote_percentage, winner))


# MIA'S CODE

# creating separate table for movie_genres, sorting by an integer id
cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_genre_id (
   id INTEGER PRIMARY KEY,
   genre TEXT UNIQUE
)
''')

# creating box_office_movies table
cursor.execute('''
CREATE TABLE IF NOT EXISTS box_office_movies (
   genre_id INTEGER,
   year INTEGER,
   title TEXT,
   revenue INTEGER,
   FOREIGN KEY (genre_id) REFERENCES movie_genre_id(id)
)
''')

# loading 25 movies at a time
with open('cache_tmdb.json', 'r') as f:
   movie_data = json.load(f)

insert_count = 0
processed_count = 0  # keeps track of records processed from the JSON file

# Fetch existing movies from the database to check for duplicates
cursor.execute("SELECT title, year FROM box_office_movies")
existing_movies = set(cursor.fetchall())  # Store as a set for fast lookup

# Open JSON files for top movies data
with open('cache_tmdb.json', 'r') as f:
   movie_data = json.load(f)

for key, movie in movie_data.items():
    if insert_count >= 25:
        break  # Stops at 25 movies

    if movie:
        genre, year = key.rsplit("-", 1)
        title = movie.get("title", "")
        revenue = movie.get("revenue", 0)

        # Skip if this movie is already in the table by checking against existing_movies set
        if (title, int(year)) in existing_movies:
            continue

        # Insert genre if it doesn't exist
        cursor.execute("INSERT OR IGNORE INTO movie_genre_id (genre) VALUES (?)", (genre,))
        cursor.execute("SELECT id FROM movie_genre_id WHERE genre = ?", (genre,))
        genre_id = cursor.fetchone()[0]

        # Insert movie into box_office_movies table
        cursor.execute('''
            INSERT INTO box_office_movies (genre_id, year, title, revenue)
            VALUES (?, ?, ?, ?)
        ''', (genre_id, int(year), title, revenue))

        insert_count += 1  # Increment insert_count after each insertion
        processed_count += 1  # Count the number of processed records

print(f"{insert_count} new movies inserted into box_office_movies.")


# END OF MIA CODE




# Create the 'yes_or_no' table to store winner status as integers (1 for 'yes' and 2 for 'no')
cursor.execute('''
CREATE TABLE IF NOT EXISTS yes_or_no (
    winner_id INTEGER PRIMARY KEY,
    winner_status TEXT UNIQUE NOT NULL
)
''')

# Insert 'yes' and 'no' into the yes_or_no table separately
cursor.execute("INSERT OR IGNORE INTO yes_or_no (winner_status) VALUES ('yes')")
cursor.execute("INSERT OR IGNORE INTO yes_or_no (winner_status) VALUES ('no')")

# Create the 'music_election' table: outer join between 'tracks' and 'election_results' on 'year'
cursor.execute('''
CREATE TABLE IF NOT EXISTS music_election AS
SELECT
   t.year,
   t.track_name AS title,
   g.genre_id,  -- Use genre_id from music_genres table
   t.popularity AS popularity,
   e.party_id,
   e.presidential_nominee_id,
   e.vice_presidential_nominee_id,
   e.electoral_vote,
   e.electoral_vote_percentage,
   e.popular_vote,
   e.popular_vote_percentage,
   -- Ensure we get the correct winner_id from yes_or_no table (1 for 'yes' and 2 for 'no')
   ws.winner_id AS winner,  -- This will insert 1 for 'yes' and 2 for 'no'
   t.release_date  -- Explicitly include release_date here
FROM tracks t
LEFT OUTER JOIN election_results e ON t.year = e.year
LEFT OUTER JOIN music_genres g ON t.genre_id = g.genre_id  -- Ensure you are joining on the correct key (genre_id, not genre_name)
LEFT OUTER JOIN yes_or_no ws ON LOWER(e.winner) = LOWER(ws.winner_status)  -- Normalize case by converting both to lowercase
GROUP BY t.year, t.track_name  -- Group by year and track_name to remove duplicates
ORDER BY t.year;

''')

# Create the 'movie_election' table: join box_office_movies, movie_genre_id, and election_results
cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_election AS
SELECT
   b.year,
   b.title,
   GROUP_CONCAT(b.genre_id) AS genre_ids,  -- Concatenate all genre_ids into a single string
   b.revenue,
   MAX(e.party_id) AS party_id,  -- Aggregate party_id
   MAX(e.presidential_nominee_id) AS presidential_nominee_id,  -- Aggregate presidential nominee ID
   MAX(e.vice_presidential_nominee_id) AS vice_presidential_nominee_id,  -- Aggregate vice-presidential nominee ID
   MAX(e.electoral_vote) AS electoral_vote,  -- Aggregate electoral vote
   MAX(e.electoral_vote_percentage) AS electoral_vote_percentage,  -- Aggregate electoral vote percentage
   MAX(e.popular_vote) AS popular_vote,  -- Aggregate popular vote
   MAX(e.popular_vote_percentage) AS popular_vote_percentage,  -- Aggregate popular vote percentage
   MAX(ws.winner_id) AS winner  -- Aggregate winner from the yes_or_no table
FROM box_office_movies b
LEFT OUTER JOIN election_results e ON b.year = e.year
LEFT OUTER JOIN yes_or_no ws ON LOWER(e.winner) = LOWER(ws.winner_status)  -- Normalize both sides to lowercase
GROUP BY b.year, b.title, b.revenue  -- Group by movie properties
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