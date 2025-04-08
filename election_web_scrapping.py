import requests
from bs4 import BeautifulSoup
import json

urls = [
    'https://www.presidency.ucsb.edu/statistics/elections/2024',
    'https://www.presidency.ucsb.edu/statistics/elections/2020',
    'https://www.presidency.ucsb.edu/statistics/elections/2016',
    'https://www.presidency.ucsb.edu/statistics/elections/2012'
]

all_election_data = []

winner_image_url = 'https://www.presidency.ucsb.edu/sites/default/files/wysiwyg_template_images/ic_check_circle_black2x.png'

for url in urls:
    print(f"Scraping data from: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    rows = soup.find_all('tr')
    election_data = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 8:
            continue

        party = cols[0].get_text(strip=True)
        president = cols[2].get_text(strip=True)
        vice_president = cols[3].get_text(strip=True)
        electoral_vote = cols[4].get_text(strip=True)
        electoral_percentage = cols[5].get_text(strip=True)
        popular_vote = cols[6].get_text(strip=True)
        popular_percentage = cols[7].get_text(strip=True)
        
        winner_image = row.find('img', src=winner_image_url)
        winner = "Yes" if winner_image else "No"
        
        if party in ['Democratic', 'Republican']:
            election_data.append({
                'Party': party,
                'Presidential Nominee': president,
                'Vice Presidential Nominee': vice_president,
                'Electoral Vote': electoral_vote,
                'Electoral Vote %': electoral_percentage,
                'Popular Vote': popular_vote,
                'Popular Vote %': popular_percentage,
                'Winner': winner
            })
    
    all_election_data.append({
        'Year': url.split('/')[-1],
        'Election Data': election_data
    })

with open('election_web_scrapping.json', 'w') as json_file:
    json.dump(all_election_data, json_file, indent=4)

print("data has been exported to 'election_web_scrapping.json'.")