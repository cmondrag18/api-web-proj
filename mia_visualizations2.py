import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.ticker as mtick
import os

# Connect to your database
conn = sqlite3.connect('sql_processing_take2.db')
cursor = conn.cursor()

# Define all 11 target genres and election years
target_genres = (
    'Sci-Fi', 'Romance', 'Documentary', 'Drama', 'Comedy',
    'Action', 'Animation', 'Adventure', 'Fantasy', 'Thriller', 'Mystery'
)
election_years = (2012, 2016, 2020, 2024)

# Step 1: Get winning party names by joining with parties table
cursor.execute('''
   SELECT e.year, p.party_name
   FROM election_results e
   JOIN parties p ON e.party_id = p.party_id
   WHERE e.winner = 'Yes' AND e.year IN (2012, 2016, 2020, 2024)
''')
winners = {row[0]: row[1] for row in cursor.fetchall()}

# Step 2: JOIN with movie_genre_id to get genre name and max revenue per genre/year
placeholders = ', '.join(['?'] * len(target_genres))
query = f'''
   SELECT b.year, g.genre, MAX(b.revenue)
   FROM box_office_movies b
   JOIN movie_genre_id g ON b.genre_id = g.id
   WHERE g.genre IN ({placeholders})
     AND b.year IN (2012, 2016, 2020, 2024)
   GROUP BY b.year, g.genre
'''
cursor.execute(query, target_genres)

# Step 3: Get top genre by revenue for each year
revenue_by_year_genre = defaultdict(list)
for year, genre, revenue in cursor.fetchall():
    revenue_by_year_genre[year].append((genre, revenue))

top_genre_per_year = {}
for year, genre_revs in revenue_by_year_genre.items():
    top_genre_per_year[year] = max(genre_revs, key=lambda x: x[1])  # (genre, revenue)

# Step 4: Prep for plotting
def format_currency(val):
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.1f}B"
    else:
        return f"${val/1_000_000:.0f}M"

years = sorted(top_genre_per_year.keys())
genres = [top_genre_per_year[year][0] for year in years]
revenues = [top_genre_per_year[year][1] for year in years]
colors = ['blue' if winners[year] == 'Democratic' else 'red' for year in years]

# Step 5: Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(years, revenues, color=colors)

plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: format_currency(x)))

for bar, genre, revenue in zip(bars, genres, revenues):
    height = bar.get_height()
    label = f"{genre}\n{format_currency(revenue)}"
    plt.text(bar.get_x() + bar.get_width()/2, height + height * 0.02, label,
             ha='center', va='bottom', fontsize=9)

plt.ylabel('Top Genre Revenue')
plt.xlabel('Election Year')
plt.title('Highest Earning Genre per Election Year by Winning Party')
plt.xticks(years)
plt.tight_layout()

# === Write top genre per year to text file ===
try:
    output_path = 'top_genre_by_year.txt'
    with open(output_path, 'w') as f:
        f.write("Top-Grossing Genre by Election Year (2012, 2016, 2020, 2024)\n\n")
        for year in years:
            genre = top_genre_per_year[year][0]
            revenue = top_genre_per_year[year][1]
            party = winners[year]
            f.write(f"{year} ({party} win): {genre} - ${revenue:,.0f}\n")
    print(f"Top genre data written to {output_path}")
except:
    print("Failed to write top genre data file.")

plt.show()
