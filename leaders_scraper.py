"""The following code scrapes Wikipedia pages and retrieves information for the leaders, past and presents, of a list of countries. Information for each leader takes the form of a dictionary.
The information for each leader is enriched with the first paragraph of their Wikipedia page."""

#Import required modules and libraries
import requests
from bs4 import BeautifulSoup
import re
import functools		#Is it still required? If not, remove it from the code.
import json

#Create a 'Session' object to make use of a single session for all the Wikipedia calls.
s = requests.Session()

#Define a function to save the results into a JSON file.
def save():
    with open('leaders.json','w') as outfile:
        json.dump(leaders_per_country, outfile)

#Create a custom cache for the url (code as provided).
cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

#Define a get_first_paragraph function, passing both the wikipedia url and the session object as arguments, to retrieve the first paragraph of each country's leaders on Wikipedia.
@hashable_cache
def get_first_paragraph(wikipedia_url, s):
    req = s.get(wikipedia_url)
    paragraphs = BeautifulSoup(req.text,"html.parser").find_all('p')
    for paragraph in paragraphs:
        if paragraph.find_all('b'):
            dirty_first_paragraph = paragraph.text
            pattern = r" \(\/.*\/\[e\] Écouter\)"				#pattern covers a single case in French, to be improved.
            first_paragraph = re.sub(pattern, "", dirty_first_paragraph)
            return first_paragraph

#Define a get_leaders function to retrieve information on each country's leaders
def get_leaders():
    root_url = 'https://country-leaders.herokuapp.com'
    country_url = 'https://country-leaders.herokuapp.com/countries'
    cookie_url = 'https://country-leaders.herokuapp.com/cookie'
    leaders_url = 'https://country-leaders.herokuapp.com/leaders'
    cookies = s.get(cookie_url).cookies
    countries = s.get(country_url, cookies=cookies)
    leaders_per_country = dict()
    for country in countries.json():
        params = {"country":country}
        leaders = s.get(leaders_url, cookies=cookies, params=params)
        wikipedia_url = ""
        if leaders.status_code != 200:
            cookies = s.get(cookie_url).cookies
            leaders = s.get(leaders_url, cookies=cookies, params=params)
        for leader in leaders.json():
            wikipedia_url = leader['wikipedia_url']
            leader['first_paragraph'] = get_first_paragraph(wikipedia_url,s)
            leader.update({'first_paragraph':get_first_paragraph(wikipedia_url,s)})
        leaders_per_country.update({country:leader})
    save()
    return leaders_per_country
    
    
    
    
    

