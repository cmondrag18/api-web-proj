import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('sql_processing_take2.db')
cursor = conn.cursor()


cursor.execute("SELECT DISTINCT year FROM box_office_movies")
print("Movie years:", cursor.fetchall())

cursor.execute("SELECT DISTINCT year FROM tracks")
print("Track years:", cursor.fetchall())


# CHANGED HERE FROM top_grossing_movies (which doesn't exist) to box_office_movies
cursor.execute("""
     SELECT 
         bom.year, 
         AVG(bom.revenue) AS avg_revenue, 
         AVG(tr.popularity) AS avg_popularity
     FROM 
         box_office_movies bom
     JOIN 
         tracks tr ON bom.year = tr.year
     GROUP BY 
         bom.year
     ORDER BY 
         bom.year;
""")

# Fetch results and organize them
results = cursor.fetchall()
years = [row[0] for row in results]
avg_revenues = [row[1] for row in results]
avg_popularities = [row[2] for row in results]

# Convert revenue to millions for better readability
avg_revenues_in_millions = [revenue / 1_000_000 for revenue in avg_revenues]

# Create subplots for revenue and popularity
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# Plot average revenue
ax1.set_xlabel('Year')
ax1.set_ylabel('Average Revenue (in Millions)', color='tab:blue')
ax1.plot(years, avg_revenues_in_millions, marker='o', linestyle='-', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.set_title('Average Movie Revenue Per Year')

# Plot average popularity
ax2.set_xlabel('Year')
ax2.set_ylabel('Average Popularity', color='tab:orange')
ax2.plot(years, avg_popularities, marker='o', linestyle='-', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')
ax2.set_title('Average Song Popularity Per Year')

plt.tight_layout()
plt.savefig('average_revenue_and_popularity.png')
plt.savefig('average_revenue_and_popularity_separate.png')
plt.show()