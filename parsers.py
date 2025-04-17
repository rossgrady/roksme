from bs4 import BeautifulSoup
import html5lib
import requests
import dateparser
#import icalendar

stopwords = ["Karaoke", "KARAOKE", "Dance Party", "DANCE PARTY", "CALENDAR", "Wild Turkey Thursday", "Private Event Upstairs", "Open Mic", "Music Trivia", "Tequila Tuesday", "Pangean", "CANCELED", "VERANDA PARTY", "DRAG BINGO"]

def retrieve(url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  response = requests.get(url, headers=headers)
  return response.text

def retrieve_tickera(url):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=headers)
  payload = {'action': 'tc_filter_events', 'tc_categories': '0', 'tc_start_date': '0', 'tc_column_number': '1', 'tc_show_excerpt': 'true', 'tc_show_number_of_posts': '200', 'tc_pagination_number': '1', 'tc_show_default_featured_image': 'true', 'tc_show_past_events': 'false'}
  real_url = url + "/wp-admin/admin-ajax.php"
  real_response = session.post(real_url, headers=headers, data=payload)
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
    event_dict['human_date'] = show_date.strftime('%a %d %b %Y')
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
      event_dict['human_date'] = show_date.strftime('%a %d %b %Y')
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
        event_string = title+" / "+opener_name
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
    event_dict['human_date'] = show_date.strftime('%a %d %b %Y')
    event_dict['more_url'] = more_url
    flag = False
    for word in stopwords:
      if word in event_string:
        flag = True
    if flag == False:
      event_array.append(event_dict)
  return event_array