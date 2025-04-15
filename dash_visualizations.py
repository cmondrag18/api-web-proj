import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('sql_processing.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        tgm.year, 
        AVG(tgm.revenue) AS avg_revenue, 
        AVG(tr.popularity) AS avg_popularity
    FROM 
        top_grossing_movies tgm
    JOIN 
        tracks tr ON tgm.year = tr.year  -- assuming 'year' column is common
    GROUP BY 
        tgm.year
    ORDER BY 
        tgm.year;
""")

results = cursor.fetchall()

years = [row[0] for row in results]
avg_revenues = [row[1] for row in results]
avg_popularities = [row[2] for row in results]

avg_revenues_in_millions = [revenue / 1_000_000 for revenue in avg_revenues]

# print(avg_revenues)
# print(avg_popularities)

fig, ax1 = plt.subplots()

ax1.set_xlabel('Year')
ax1.set_ylabel('Average Revenue (in Millions)', color='tab:blue')
ax1.plot(years, avg_revenues_in_millions, marker='o', linestyle='-', color='tab:blue', label='Average Revenue')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Average Popularity', color='tab:orange')
ax2.plot(years, avg_popularities, marker='o', linestyle='-', color='tab:orange', label='Average Popularity')
ax2.tick_params(axis='y', labelcolor='tab:orange')

plt.title('Average Movie Revenue and Song Popularity Per Year')
fig.tight_layout()

plt.savefig('average_revenue_and_popularity.png')

plt.show()



