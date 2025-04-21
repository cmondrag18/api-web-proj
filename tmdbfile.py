import requests
import json
import os


API_KEY = 'd7310332d3cce9353cbd1ed056aa7e1e'
CACHE_FILE = 'cache_tmdb.json'


# 11 genres from TMDb
GENRES = {
    'Sci-Fi': 878,
    'Romance': 10749,
    'Drama': 18,
    'Comedy': 35,
    'Documentary': 99,
    'Action': 28,
    'Animation': 16,
    'Adventure': 12,
    'Fantasy': 14,
    'Thriller': 53,
    'Mystery': 9648  
}



# 5 election years ±1 = 15 years total
ELECTION_YEARS = [
   2007, 2008, 2009,
   2011, 2012, 2013,
   2015, 2016, 2017,
   2019, 2020, 2021,
   2023, 2024, 2025
]




def get_json_content(filename):
   try:
       with open(filename, 'r') as f:
           return json.load(f)
   except:
       return {}




def save_cache(cache, filename):
   try:
       with open(filename, 'w') as f:
           json.dump(cache, f, indent=4)
   except:
       print("Error saving cache.")




def fetch_genre_ids():
   url = "https://api.themoviedb.org/3/genre/movie/list"
   params = {"api_key": API_KEY}
   response = requests.get(url, params=params)
   if response.status_code == 200:
       genres = response.json().get("genres", [])
       print("TMDb Genre IDs:")
       for genre in genres:
           print(f"{genre['name']}: {genre['id']}")
   else:
       print(f"Error fetching genres: {response.status_code}")




def discover_movies_by_genre_year(genre_id, year):
   url = "https://api.themoviedb.org/3/discover/movie"
   params = {
       "api_key": API_KEY,
       "with_genres": genre_id,
       "primary_release_year": year,
       "sort_by": "revenue.desc",
       "page": 1
   }
   response = requests.get(url, params=params)
   if response.status_code == 200:
       return response.json().get('results', [])
   else:
       print(f"Error fetching data from TMDb: {response.status_code}")
       return []




def get_movie_details(movie_id):
   url = f"https://api.themoviedb.org/3/movie/{movie_id}"
   params = {"api_key": API_KEY}
   response = requests.get(url, params=params)
   if response.status_code == 200:
       return response.json()
   else:
       return None




def update_cache():
   cache = get_json_content(CACHE_FILE)
   for genre_name, genre_id in GENRES.items():
       for year in ELECTION_YEARS:
           key = f"{genre_name}-{year}"
           if key in cache and cache[key]:  # avoid duplicates
               continue
           print(f"Fetching {genre_name} movies for {year}...")
           movies = discover_movies_by_genre_year(genre_id, year)
           top_movie = None
           max_revenue = -1
           for movie in movies:
               details = get_movie_details(movie['id'])
               if details and details.get('revenue', 0) > max_revenue:
                   max_revenue = details['revenue']
                   top_movie = {
                       'title': details.get('title'),
                       'year': details.get('release_date', '')[:4],
                       'revenue': details.get('revenue')
                   }
           if top_movie:
               cache[key] = top_movie
               save_cache(cache, CACHE_FILE)
   return cache

def main():
   cache = update_cache()
   print("\n=== Summary of Cached Movies ===")
   for genre_name in GENRES:
       for year in ELECTION_YEARS:
           key = f"{genre_name}-{year}"
           movie = cache.get(key)
           if movie:
               print(f"{genre_name} ({year}): {movie['title']} - ${movie['revenue']:,}")
           else:
               print(f"{genre_name} ({year}): No data.")
   print(f"\nTotal movies cached: {len(cache)} (Expected: 165)")

if __name__ == "__main__":
   main()
