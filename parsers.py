from bs4 import BeautifulSoup
import html5lib
import requests
import dateparser
import icalendar
import json

# we really do need parser-specific stopwords, sigh

stopwords = ["Karaoke", "KARAOKE", "Dance Party", "DANCE PARTY", "CALENDAR", "Wild Turkey Thursday", "Private Event Upstairs", "Open Mic", "Music Trivia", "Tequila Tuesday", "Pangean", "CANCELED", "VERANDA PARTY", "DRAG BINGO", "Movie Loft", "BYOV", "COMEDY NIGHT", "NEPTUNES COMEDY", "CLOSED FOR A PRIVATE EVENT", "BIRTHDAY BASH", "BROOKLYN BARISTA", "BRUNCH SOCIETY", "brunch society", "VINYL DECODED", "Emo Night", "Comedy Show", "DANCE NIGHT", "The Glitter Hour", "Triangle Film", "EDM Weekly Party", "Goth Night", "Amateur Burlesque", "Broadway"]

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
      opener_name = opener.string.strip()
      if len(opener_name) > 0:
        event_string = title+" w/ "+opener_name
    venue = event.find(class_="venueLink")
    if venue:
      venue_url = venue['href']
      venue_name = venue.string.strip()
    date = event.find(class_="singleEventDate").string.strip()
    show_date = dateparser.parse(date)
    more_url = event.find(class_="rhp-event__cta__more-info--list").a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def tribe_parser(venue_name, url):
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
      date = event.find(class_="tribe-events-calendar-list__event-date-tag-datetime")['datetime']
      show_date = dateparser.parse(date)
      event_dict['venue_name'] = venue_name
      event_dict['venue_url'] = venue_url
      event_dict['event_string'] = event_string
      event_dict['event_date'] = show_date
      event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
      event_dict['more_url'] = more_url
      flag = False
      for word in stopwords:
        if word in event_string:
          flag = True
      if flag == False:
        event_array.append(event_dict)
  return event_array

def ical_parser(venue_name, url):
  ical_content = retrieve(url)
  # now we need to parse that ical!
  calendar = icalendar.Calendar.from_ical(ical_content)
  for event in calendar.events:
    print(event.get("SUMMARY"))
    print(event.get("DTSTART"))
    print(event.get("DESCRIPTION"))
    print("---")

def tickera_parser(venue_name, url):
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
    date = event.find(class_="tc-event-date").span.string.strip()
    show_date = dateparser.parse(date)
    more_url = event.find('h4').a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array


def mec_parser(venue_name, url):
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
    date = event.find(class_="mec-start-date-label").string.strip()
    show_date = dateparser.parse(date)
    more_url = event.find(class_='mec-event-title').a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def eventprime_parser(venue_name, url):
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
    date = event.find(class_="date").string.strip()
    show_date = dateparser.parse(date)
    more_url = event.find(class_='body').a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def avia_parser(venue_name, url):
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
    date = event.find(class_="showdate").string.strip()
    show_date = dateparser.parse(date)
    more_url = title.a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def sqs_parser(venue_name, url):
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
    date = date_month + " " + date_day
    show_date = dateparser.parse(date)
    more_url_rel = title['href']
    more_url_rel_rel = more_url_rel.split('/')
    more_url = url + "/" + more_url_rel_rel[2]
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def seetickets_parser(venue_name, url):
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
      date = event.find(class_="event-date").string.strip()
      show_date = dateparser.parse(date)
      more_url = title.a['href']
      event_dict['venue_name'] = venue_name
      event_dict['venue_url'] = venue_url
      event_dict['event_string'] = event_string
      event_dict['event_date'] = show_date
      event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
      event_dict['more_url'] = more_url
      flag = False
      for word in stopwords:
        if word in event_string:
          flag = True
      if flag == False:
        event_array.append(event_dict)
  return event_array

def freemius_parser(venue_name, url):
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
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = event['Event']['url']
    flag = False
    for word in stopwords:
      if word in event_dict['event_string']:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def dpac_parser(venue_name, url):
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
    date_month = date_container.find(class_="m-date__month").string.strip()
    date_day = date_container.find(class_="m-date__day").string.strip()
    date_year = date_container.find(class_="m-date__year").string.strip()
    date = date_month + " " + date_day + date_year
    show_date = dateparser.parse(date)
    more_url = title['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array

def carolina_parser(venue_name, url):
  html_content = retrieve_carolina(url)
  print(html_content)
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
    date = date_month + " " + date_day
    show_date = dateparser.parse(date)
    more_url = event.a['href']
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = "https://carolinatheatre.org/events/"
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%A, %B %d, %Y')
    event_dict['more_url'] = more_url
    flag = False
    category = event.find(class_="event__categories").string.strip()
    if category == "Music":
      flag = False
    else:
      flag = True
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array