from bs4 import BeautifulSoup
import html5lib
import requests
import dateparser
import json
from datetime import date, datetime
from urllib.parse import urlparse

stopwords = ["karaoke", "dance party", "dance night", "open mic", "comedy night", "burlesque"]

venue_stopwords = {
  "Durham Performing Arts Center" : ["sesame street", "broadway", "stardew valley", "twilight in concert", "neil degrasse tyson", "ballet", "musical", "dave ramsey", "brit floyd", "get the led out", "louis ck", "vision of queen", "rocket man"],
  "Martin Marietta Center" : ["indian dance", "ballet", "symphony", "dance recital", "ken burns", "concert", "opera"],
  "Koka Booth Amphitheatre" : ["bourbon & bbq", "wine & fire", "symphony"],
  "Lincoln Theatre" : ["tribute", "bring out yer dead", "ultimate led zeppelin"],
  "Missy Lane's Assembly Room" : ["closed for a private event", "birthday bash", "brooklyn barista", "brunch society", "vinyl decoded", "exclusive preview", "vin", "tribute band"],
  "Cat’s Cradle" : ["school of rock"],
  "The Cave" : ["calendar"], 
  "Cat’s Cradle Back Room" : ["school of rock"], 
  "Cat’s Cradle Back Yard" : [],
  "Duke University East Campus" : [],
  "Haw River Ballroom" : [],
  "Local 506" : [],
  "Sharp 9 Gallery Jazz Club" : ["student combo"], 
  "The Fruit" : ["fruit flea", "rhizome comedy"], 
  "Carolina Theatre" : ["a tribute to"], 
  "Motorco Music Hall" : ["canceled", "party", "chappell roan", "drag bingo", "adult science fair", "motown-inspired"], 
  "The Pinhook" : ["russell lacy", "burlesque", "blends with friends"], 
  "Rubies" : ["byov", "renaissance disko", "adulting"],
  "Shadowbox Studio" : ["movie loft", "scapegoat initiative"],
  "The Ritz Raleigh" : [],
  "The Pour House" : ["superbloom comedy", "tribute experience", "a tribute to", "tribute night", "tributes to", "listening party"],
  "The Night Rider" : [],
  "The Rialto" : [],
  "Kings" : [],
  "Wake Forest Listening Room" : [],
  "Neptunes" : ["goth party", "munjo", "guitar hero iii", "neptunes comedy", "comedy taping", "chappell rodeo"],
  "Ruby Deluxe" : ["glitter hour", "sub rosa", "animazement"],
  "Slim's" : ["wild turkey thursday", "private event upstairs", "private mixer upstairs", "music trivia", "tequila tuesday", "pangean"],
  "The Wicked Witch" : ["safe word", "triangle film", "goth night"],
  "Red Hat Amphitheater" : [],
  "Fletcher Opera Theater" : ["indian dance", "ballet", "symphony", "recital", "ken burns", "concert", "opera", "raleigh ringers"],
  "Memorial Auditorium" : ["indian dance", "ballet", "symphony", "dance recital", "ken burns", "concert", "opera"],
  "Meymandi Concert Hall" : ["indian dance", "ballet", "symphony", "dance recital", "ken burns", "concert", "opera"], 
  "Kennedy Theater" : ["mixer", "indian dance", "ballet", "symphony", "dance recital", "ken burns", "concert", "opera"]
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

def retrieve_tickera(url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=headers)
  payload = {'action': 'tc_filter_events', 'tc_categories': '0', 'tc_start_date': '0', 'tc_column_number': '1', 'tc_show_excerpt': 'true', 'tc_show_number_of_posts': '200', 'tc_pagination_number': '1', 'tc_show_default_featured_image': 'true', 'tc_show_past_events': 'false'}
  real_url = url + "/wp-admin/admin-ajax.php"
  real_response = session.post(real_url, headers=headers, data=payload)
  return real_response.text

def retrieve_carolina(url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=headers)
  real_url = "https://carolinatheatre.org/wp-admin/admin-ajax.php?action=event_filter&events=all"
  real_response = session.get(real_url, headers=headers)
  return real_response.text

def rhp_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events = soup(class_="rhpSingleEvent")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_="rhp-event__title--list").string.strip()
    event_string = title
    venue_url = url
    opener = event.find(class_="rhp-event__subheader--list")
    if(opener):
      if len(opener) > 0 and opener.string:
        opener_name = opener.string.strip()
        if len(opener_name) > 0:
          if "w/" in opener_name:
            event_string = title+" "+opener_name
          else:
            event_string = title+" w/ "+opener_name
      else:
        continue
    venue = event.find(class_="venueLink")
    if venue:
      venue_url = venue['href']
      venue_name = venue.string.strip()
    if venue_name == "the Pinhook":
      venue_name = "The Pinhook"
    raw_date = event.find(class_="singleEventDate").string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = event.find(class_="rhp-event__cta__more-info--list").a['href']
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

def tribe_parser(venue_name, url):
  source = venue_name
  event_array = []
  for i in range(1,7):
    if i < 2:
      paginated_url = url
    else:
      paginated_url = url + "page/" + str(i) + "/"
    html_content = retrieve(paginated_url)
    soup = BeautifulSoup(html_content, 'html5lib')
    if soup(class_="tribe-events-c-messages__message-list-item"):
      messages = soup(class_="tribe-events-c-messages__message-list-item")
      if messages[0].string.strip() == "There were no results found.":
        return event_array
    events = soup(class_="tribe-events-calendar-list__event-row")
    for event in events:
      event_dict = {}
      more_url = event.find(class_="tribe-events-calendar-list__event-title").a['href']
      event_string = event.find(class_="tribe-events-calendar-list__event-title-link").string.strip()
      venue_url = url
      openers_array = event.find_all(class_="bands-row")
      if(openers_array):
        if len(openers_array) > 0:
          for opener in openers_array:
            opener_name = opener.string.strip()
            if opener_name not in event_string:
              event_string = event_string+" / "+opener_name
      raw_date = event.find(class_="tribe-events-calendar-list__event-date-tag-datetime")['datetime']
      show_date = dateparser.parse(raw_date)
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

def tickera_parser(venue_name, url):
  source = venue_name
  html_content = retrieve_tickera(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events = soup(class_="tc-single-event")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find('h4').a.string.strip()
    event_string = title
    venue_url = url
    opener = event.find(class_="with")
    if(opener):
      opener_name = opener.next_sibling.strip()
      if len(opener_name) > 0:
        event_string = event_string+" / "+opener_name
    venue = event.find(class_="venueLink")
    if venue:
      venue_url = venue['href']
      venue_name = venue.string.strip()
    raw_date = event.find(class_="tc-event-date").span.string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = event.find('h4').a['href']
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
    if not isinstance(show_date, datetime):
      continue
    more_url = event.find(class_='mec-event-title').a['href']
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

def eventprime_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find("table", id="Shows")
  events = events_container.find_all("tr")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find("h3")
    event_string = title.string.strip()
    venue_url = url
    opener = title.find_next_sibling("h4")
    if(opener):
      opener_name = opener.string.strip()
      if len(opener_name) > 0:
        event_string = event_string + " " + opener_name
    raw_date = event.find(class_="date").string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = event.find(class_='body').a['href']
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

def avia_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(id="after_section_1")
  events = events_container.find_all(class_="post-entry-type-standard")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_="post-title")
    event_string = ""
    for string in title.a.stripped_strings:
      event_string = event_string + string + " "
    venue_url = url
    opener = event.find(class_="otherbands").h3
    if(opener):
      if len(opener) > 0:
        if "w/" in opener.string:
          event_string = event_string + opener.string.strip()
        else:
          event_string = event_string + "/ " + opener.string.strip()
    raw_date = event.find(class_="showdate").string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = title.a['href']
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

def sqs_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="eventlist--upcoming")
  events = events_container.find_all(class_="eventlist-event--upcoming")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_="eventlist-title-link")
    event_string = title.string.strip()
    venue_url = url
    opener_container = event.find(class_="eventlist-description")
    if(opener_container):
      opener = opener_container.find(class_="sqs-html-content").p
      if len(opener) > 0:
        if opener.string:
          if "w/" in opener.string:
            event_string = event_string + " " + opener.string.strip()
          elif "featuring" in opener.string:
            event_string = event_string + opener.string.strip()
    date_container = event.find(class_="eventlist-datetag-inner")
    date_month = date_container.find(class_="eventlist-datetag-startdate--month").string.strip()
    date_day = date_container.find(class_="eventlist-datetag-startdate--day").string.strip()
    raw_date = date_month + " " + date_day
    show_date = dateparser.parse(raw_date)
    more_url_rel = title['href']
    more_url_rel_rel = more_url_rel.split('/')
    more_url = url + "/" + more_url_rel_rel[2]
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

def seetickets_parser(venue_name, url):
  source = venue_name
  event_array = []
  for i in range(1,7):
    if i < 2:
      paginated_url = url
    else:
      paginated_url = url + "?list1page=" + str(i)
    html_content = retrieve(paginated_url)
    soup = BeautifulSoup(html_content, 'html5lib')
    if soup(id="cf-error-details"):
      return event_array
    if soup(class_="no-events"):
      return event_array
    events_container = soup.find(class_="seetickets-list-events")
    events = events_container.find_all(class_='seetickets-list-event-container')
    for event in events:
      event_dict = {}
      title = event.find(class_='event-title')
      event_string = title.a.string.strip()
      venue_url = url
      raw_date = event.find(class_="event-date").string.strip()
      show_date = dateparser.parse(raw_date)
      more_url = title.a['href']
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

def freemius_parser(venue_name, url):
  source = venue_name
  json_content = retrieve(url)
  data = json.loads(json_content)
  event_array = []
  for event in data['data']:
    event_dict = {}
    show_date = dateparser.parse(event['Event']['start'])
    event_dict['venue_name'] = venue_name
    if venue_name == "Ruby Deluxe":
      event_dict['venue_url'] = "https://queerraleigh.com/home/ruby-deluxe/"
    elif venue_name == "The Night Rider":
      event_dict['venue_url'] = "https://queerraleigh.com/home/the-night-rider/"
    elif venue_name == "The Wicked Witch":
      event_dict['venue_url'] = "https://queerraleigh.com/home/the-wicked-witch/"
    event_dict['event_string'] = event['Event']['name']
    event_dict['event_date'] = show_date.date()
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = event['Event']['url']
    event_dict['source'] = source
    flag = filter_on_stopwords(venue_name, event_dict['event_string'], show_date.date())
    if flag == False:
      event_array.append(event_dict)
  return event_array

def dpac_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(id="list")
  events = events_container.find_all(class_="eventItem")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_="title").a
    event_string = title.string.strip()
    venue_url = url
    opener = event.find(class_="tagline")
    if(opener):
      if len(opener) > 0:
        event_string = event_string + " - " + opener.string.strip()
    date_container = event.find(class_="date")
    if date_container.find(class_="m-date__month") != None:
      date_month = date_container.find(class_="m-date__month").string.strip()
    if date_container.find(class_="m-date__day") != None:
      date_day = date_container.find(class_="m-date__day").string.strip()
    if date_container.find(class_="m-date__year") != None:
      date_year = date_container.find(class_="m-date__year").string.strip()
    if date_month and date_day and date_year:
      raw_date = date_month + " " + date_day + date_year
    else:
      continue
    show_date = dateparser.parse(raw_date)
    more_url = title['href']
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

def carolina_parser(venue_name, url):
  source = venue_name
  html_content = retrieve_carolina(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="card__wrapper")
  events = events_container.find_all(class_="eventCard")
  event_array = []
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
    event_dict['venue_url'] = "https://carolinatheatre.org/events/"
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date.date()
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    event_dict['source'] = source
    flag = filter_on_stopwords(venue_name, event_string, show_date.date())
    category = event.find(class_="event__categories").string.strip()
    if category != "Music":
      flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def opendate_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="form-row")
  events = events_container.find_all(class_="card-body")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find("p", class_="text-dark")
    event_string = ""
    for string in title.a.stripped_strings:
      event_string = event_string + string + " "
    raw_date = title.find_next_sibling("p").string.strip()
    show_date = dateparser.parse(raw_date)
    more_url = title.a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = "https://www.durhamfruit.com/"
    event_dict['event_string'] = event_string.strip()
    event_dict['event_date'] = show_date.date()
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    event_dict['source'] = source
    flag = filter_on_stopwords(venue_name, event_string, show_date.date())
    if flag == False:
      event_array.append(event_dict)
  return event_array

def clickgobuynow_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(class_="panel")
  events = events_container.find_all(class_='row')
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_='title').string.strip()
    event_string = title
    venue_url = "https://www.durhamjazzworkshop.org/concerts.html"
    date_container = event.find(class_="event-date")
    date_month = date_container.find(class_="event-month").string.strip()
    date_day = date_container.find(class_="event-day").string.strip()
    raw_date = date_month + " " + date_day
    show_date = dateparser.parse(raw_date)
    more_url = event.find(class_='button-group').find(class_='secondary')['href']
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

def chakra_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events_container = soup.find(attrs={"data-automation": "shows-grid"})
  events = events_container.find_all(class_='chakra-card__footer')
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_='chakra-text').string.strip()
    event_string = title
    venue_url = url
    raw_date = ""
    for child in event.find("time").css.filter('p'):
      if child.string.strip() == "Multi Day":
        raw_date = "Jan 01 1990"
        break
      else:
        raw_date = raw_date + child.string.strip() + " "
    show_date = dateparser.parse(raw_date)
    more_url = event.find(class_='chakra-linkbox__overlay')['href']
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

def rcc_parser(venue_name, url):
  source = venue_name
  event_array = []
  for i in range(2):
    if i > 0 and source == "Red Hat Amphitheater":
      return event_array
    else:
      paginated_url = url + "/?page=" + str(i)
      html_content = retrieve(paginated_url)
      soup = BeautifulSoup(html_content, 'html5lib')
      events_container = soup.find(class_="view-rcc-events")
      events = events_container.find_all(class_='node--type-event')
      for event in events:
        event_dict = {}
        title = event.find(class_='event__title').a
        event_string = title.span.string.strip()
        venue_url = url
        venue_name = event.find(class_='event__field-venue').string.strip()
        date_container = event.find(class_="date__set--start")
        date_month = date_container.find(class_="date__month-abbr").string.strip()
        date_day = date_container.find(class_="date__day").string.strip()
        raw_date = date_month + " " + date_day
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

def mrl_parser(venue_name, url):
  source = venue_name
  html_content = retrieve(url)
  soup = BeautifulSoup(html_content, 'html5lib')
  events = soup(class_="post-event")
  event_array = []
  for event in events:
    event_dict = {}
    title = event.find(class_="title").string.strip()
    event_string = title
    more_url = event.find(class_="post-header")['href']
    event_details = retrieve(more_url)
    details_soup = BeautifulSoup(event_details, 'html5lib')
    venue = details_soup.find(class_="location-link")
    if venue:
      venue_url = venue['href']
      venue_name = venue.string.strip()
    raw_date = ""
    for string in event.find(class_="event-date-alt").stripped_strings:
      raw_date = raw_date + string
    show_date = dateparser.parse(raw_date)
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