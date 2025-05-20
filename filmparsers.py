from bs4 import BeautifulSoup
import html5lib
import requests
import dateparser
import json
from datetime import date
from urllib.parse import urlparse

stopwords = []

venue_stopwords = {
  "Carolina Theatre" : [], 
  "Shadowbox Studio" : [],
  }

def filter_on_stopwords(venue_name, event_string, show_date):
  now = date.today()
  if show_date < now:
    return True
  if venue_name in venue_stopwords:
    custom_stopwords = stopwords + venue_stopwords[venue_name]
  else:
    custom_stopwords = stopwords
  for word in custom_stopwords:
    if word in event_string.lower():
      print("found", event_string, "at", venue_name, "in stopwords")
      return True
  return False

def retrieve(url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=headers)
  return response.text

def retrieve_carolina(url, real_url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=headers)
  real_response = session.get(real_url, headers=headers)
  return real_response.text


def mec_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="mec-event-list-standard")
  events = events_container.find_all(class_='mec-event-article')
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_='mec-event-title').a.string.strip()
    event_string = title
    venue_url = url
    raw_date = event.find(class_="mec-start-date-label").string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = event.find(class_='mec-event-title').a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date.date()
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    event_dict['source'] = source
    if "Movie Loft" in event_string:
      event_array.append(event_dict)
  return event_array

def carolina_parser(venue_name, url):
  source = venue_name
  urls = [{'source':'now', 'url': "https://carolinatheatre.org/wp-admin/admin-ajax.php?action=film_filter&events=now-playing"}, 
          {'source':'soon', 'url': "https://carolinatheatre.org/wp-admin/admin-ajax.php?action=film_filter&events=coming-soon"}]
  event_array = []
  for real_url in urls:
    html_content = retrieve_carolina(url, real_url['url'])
    soup = BeautifulSoup(html_content, 'html5lib')
    events_container = soup.find(class_="card__wrapper")
    events = events_container.find_all(class_="eventCard")
    source = real_url['source']
    for event in events:
      event_dict = {}
      title = event.find(class_="card__title")
      event_string = title.string.strip()
      date_container = event.find(class_="event__dateBox")
      date_month = date_container.find(class_="month").string.strip()
      date_day = date_container.find(class_="day").string.strip()
      raw_date = date_month + " " + date_day
      show_date = dateparser.parse(raw_date)
      more_url = event.a['href']
      event_dict['venue_name'] = venue_name
      event_dict['venue_url'] = "https://carolinatheatre.org/films/"
      event_dict['event_string'] = event_string
      event_dict['event_date'] = show_date.date()
      event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
      event_dict['more_url'] = more_url
      event_dict['source'] = source
      flag = filter_on_stopwords(venue_name, event_string, show_date.date())
      if flag == False:
        event_array.append(event_dict)
  return event_array

def dss_parser(venue_name, url):
  source = venue_name
  event_array = []
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="view-screen-society-views")
  events = events_container.find_all(class_='node--type-event-screen-society')
  for event in events:
    event_dict = {}
    title = event.find(class_='h3').a
    event_string = title.string.strip()
    venue_url = url
    venue_name = event.find(class_='field-label-inline').next_sibling.strip()
    raw_date = event.find(class_='datetime').string.strip()
    show_date = dateparser.parse(raw_date)
    more_url_rel = title['href']
    url_parts = urlparse(url)
    new_url = url_parts._replace(path=more_url_rel)
    more_url = new_url.geturl()
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date.date()
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    event_dict['source'] = source
    flag = filter_on_stopwords(venue_name, event_string, show_date.date())
    if flag == False:
      event_array.append(event_dict)
  return event_array