import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.ticker as mtick


# Connect to DB
conn = sqlite3.connect('sql_processing_clean.db')
cursor = conn.cursor()


# Query for average revenue per genre, grouped by winning party
cursor.execute('''
   SELECT
   g.genre,
   e.party,
   b.revenue
FROM box_office_movies b
JOIN movie_genre_id g ON b.genre_id = g.id
JOIN election_results e ON b.year = e.year
WHERE e.winner = 'Yes'
 AND b.year IN (2012, 2016, 2020, 2024)
 AND g.genre IN ('Sci-Fi', 'Romance', 'Drama', 'Comedy', 'Documentary', 'Action', 'Animation')
''')


rows = cursor.fetchall()


# Group by (party, genre)
revenue_data = {
   'Democratic': defaultdict(list),
   'Republican': defaultdict(list)
}


for genre, party, revenue in rows:
   if party in revenue_data:
       revenue_data[party][genre].append(revenue)


# Define genre order
genres = ['Sci-Fi', 'Romance', 'Drama', 'Comedy', 'Documentary', 'Action', 'Animation']
democrat_avgs = []
republican_avgs = []


for genre in genres:
   d_revs = revenue_data['Democratic'].get(genre, [])
   r_revs = revenue_data['Republican'].get(genre, [])
  
   d_avg = sum(d_revs) / len(d_revs) if d_revs else 0
   r_avg = sum(r_revs) / len(r_revs) if r_revs else 0


   democrat_avgs.append(d_avg)
   republican_avgs.append(r_avg)


# Plotting
x = range(len(genres))
width = 0.35


plt.figure(figsize=(10, 6))
plt.bar([i - width/2 for i in x], democrat_avgs, width=width, label='Democratic Wins', color='blue')
plt.bar([i + width/2 for i in x], republican_avgs, width=width, label='Republican Wins', color='red')


# Y-axis formatting
def format_currency(value):
   if value >= 1_000_000_000:
       return f"${value / 1_000_000_000:.1f}B"
   else:
       return f"${value / 1_000_000:.0f}M"


plt.ylabel('Average Revenue')
plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: format_currency(x)))




# Bar labels
for i in range(len(genres)):
   if democrat_avgs[i] > 0:
       plt.text(i - width/2, democrat_avgs[i], f"${democrat_avgs[i]/1_000_000:.0f}M",
                ha='center', va='bottom', fontsize=8, color='blue')
   if republican_avgs[i] > 0:
       plt.text(i + width/2, republican_avgs[i], f"${republican_avgs[i]/1_000_000:.0f}M",
                ha='center', va='bottom', fontsize=8, color='red')


# Title and labels
plt.title('Avg Revenue of Top-Grossing Movies by Genre\nDuring Winning Party Election Years (2012–2024)')
plt.xlabel('Genre')
plt.xticks(ticks=x, labels=genres)
plt.legend()
plt.tight_layout()
plt.show()
