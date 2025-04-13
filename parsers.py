from bs4 import BeautifulSoup
import html5lib
import requests
import dateparser

def rhp_parser(venue_name, url, headers):
  response = requests.get(url, headers=headers)
  html_content = response.text
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
    event_array.append(event_dict)
  return event_array


def tribe_parser(venue_name, url, headers):
  response = requests.get(url, headers=headers)
  html_content = response.text
  soup = BeautifulSoup(html_content, 'html5lib')
  events = soup(class_="tribe-events-calendar-list__event-row")
  event_array = []
  for event in events:
    event_dict = {}
    more_url = event.find(class_="tribe-events-calendar-list__event-title").a['href']
    event_string = event.find(class_="tribe-events-calendar-list__event-title-link").string.strip()
    venue_url = url
    openers_array = event.find_all(class_="bands-row")
    if(openers_array):
      print(openers_array)
      if len(openers_array) > 0:
        for opener in openers_array:
          print(opener)
          opener_name = opener.string.strip()
          event_string = event_string+", "+opener_name
    #venue = event.find(class_="venueLink")
    #if venue:
    #  venue_url = venue['href']
    #  venue_name = venue.string.strip()
    date = event.find(class_="tribe-events-calendar-list__event-date-tag-datetime")['datetime']
    show_date = dateparser.parse(date)
    
    event_dict['venue_name'] = venue_name
    event_dict['venue_url'] = venue_url
    event_dict['event_string'] = event_string
    event_dict['event_date'] = show_date
    event_dict['human_date'] = show_date.strftime('%a %d %b %Y')
    event_dict['more_url'] = more_url
    event_array.append(event_dict)
  return event_array