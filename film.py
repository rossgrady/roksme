from filmparsers import mec_parser, carolina_parser, dss_parser
from operator import itemgetter
from datetime import date
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("roksme_films.html")

venues_list = [
  {'name':"Shadowbox Studio", 'url':'https://shadowboxstudio.org/events/', 'parser': mec_parser}, 
  {'name': 'Carolina Theatre', 'url': 'https://carolinatheatre.org/films/', 'parser': carolina_parser},
  {'name':"Duke Screen/Society", 'url': 'https://cinematicarts.duke.edu/screensociety/schedule', 'parser': dss_parser},
  ]

def dedupe(events_arr):
  print("deduping", len(events_arr), "events")
  working_date = events_arr[0]['human_date']
  working_venue = events_arr[0]['venue_name']
  temp_arr = []
  return_arr = []
  for event in events_arr:
    if (event['venue_name'] != working_venue) or (event['human_date'] != working_date):
      if len(temp_arr) < 2:
        return_arr = return_arr + temp_arr
      else:
        seen_now = False
        for temp_event in temp_arr:
          if temp_event['source'] == 'now':
            seen_now = True
        for temp_event in temp_arr:
          if seen_now == True:
            if temp_event['source'] == 'now':
              return_arr.append(temp_event)
          else:
            return_arr.append(temp_event)
      temp_arr = []
      temp_arr.append(event)
      working_venue = event['venue_name']
      if event['human_date'] != working_date:
        working_date = event['human_date']
    else:
      temp_arr.append(event)
  # gotta do it one more time when you exit the loop:
  if len(temp_arr) < 2:
    return_arr = return_arr + temp_arr
  else:
    seen_now = False
    for temp_event in temp_arr:
      if temp_event['source'] == 'now':
        seen_now = True
    for temp_event in temp_arr:
      if seen_now == True:
        if temp_event['source'] == 'now':
          return_arr.append(temp_event)
      else:
        return_arr.append(temp_event)
  print("returning", len(return_arr), "events")
  return return_arr

def main():
  events_array = []
  for venue in venues_list:
    venue_array = venue['parser'](venue['name'], venue['url'])
    print("working on", venue['name'], ". . . found", len(venue_array), "events")
    events_array = events_array + venue_array
  events_sorted = sorted(events_array, key=itemgetter('event_date', 'venue_name'))
  events_deduped = dedupe(events_sorted)
  today = date.today().strftime('%A, %B %d, %Y')
  template.stream(events=events_deduped, county="all", today=today).dump('films.html')

main()
