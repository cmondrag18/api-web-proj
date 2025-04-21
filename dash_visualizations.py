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

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# Plot Average Revenue on ax1
ax1.set_xlabel('Year')
ax1.set_ylabel('Average Revenue (in Millions)', color='tab:blue')
ax1.plot(years, avg_revenues_in_millions, marker='o', linestyle='-', color='tab:blue', label='Average Revenue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.set_title('Average Movie Revenue Per Year')

# Plot Average Popularity on ax2
ax2.set_xlabel('Year')
ax2.set_ylabel('Average Popularity', color='tab:orange')
ax2.plot(years, avg_popularities, marker='o', linestyle='-', color='tab:orange', label='Average Popularity')
ax2.tick_params(axis='y', labelcolor='tab:orange')
ax2.set_title('Average Song Popularity Per Year')

# Adjust the layout to prevent overlap
plt.tight_layout()

# Save the figure
plt.savefig('average_revenue_and_popularity.png')
plt.savefig('average_revenue_and_popularity_separate.png')

# Show the plot
plt.show()
