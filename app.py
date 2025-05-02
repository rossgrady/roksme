from parsers import rhp_parser, tribe_parser, tickera_parser, eventprime_parser, mec_parser, avia_parser, sqs_parser, seetickets_parser, freemius_parser, dpac_parser, carolina_parser, opendate_parser, clickgobuynow_parser, chakra_parser, rcc_parser, mrl_parser
from operator import itemgetter
from datetime import date
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("roksme_index.html")

venues_list = [
  {'name':"Koka Booth Amphitheatre", 'url': 'https://www.boothamphitheatre.com/events/all', 'parser': dpac_parser},
  {'name':"Red Hat Amphitheater", 'url': 'https://www.redhatamphitheater.com/calendar', 'parser': rcc_parser},
  {'name':"Martin Marietta Center", 'url': 'https://www.martinmariettacenter.com/event-calendar', 'parser': rcc_parser},
  {'name':"Cat's Cradle", 'url':'https://catscradle.com/events/?view=list', 'parser':rhp_parser}, 
  {'name': "Local 506", 'url':'https://local506.com/events/?view=list', 'parser':rhp_parser}, 
  {'name':"The Pinhook", 'url':'https://thepinhook.com/events/?view=list', 'parser':rhp_parser}, 
  {'name':"Slim's", 'url':'https://slimsraleigh.com/calendar/list/', 'parser': tribe_parser},
  {'name':"The Cave", 'url':'https://caverntavern.com/calendar/list/', 'parser': tribe_parser}, 
  {'name':"Motorco Music Hall", 'url':'https://motorcomusic.com/', 'parser': tickera_parser}, 
  {'name':"Shadowbox Studio", 'url':'https://shadowboxstudio.org/events/', 'parser': mec_parser}, 
  {'name':"Kings", 'url': 'https://www.kingsraleigh.com/', 'parser': eventprime_parser}, 
  {'name': 'Rubies', 'url':'https://rubiesnc.com/', 'parser':avia_parser}, 
  {'name':"Neptunes", 'url': 'https://www.neptunesraleigh.com/events', 'parser': sqs_parser}, 
  {'name':"Missy Lane's Assembly Room", 'url':'https://www.missylanes.com/schedule', 'parser': sqs_parser}, 
  {'name':"The Pour House", 'url': 'https://pourhouseraleigh.com/calendar/', 'parser': seetickets_parser}, 
  {'name': "Ruby Deluxe", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3c2-fa60-4db7-89a5-113d0ad1214d/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, 
  {'name': "The Night Rider", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3da-d7a8-4862-9049-57fd0ad1e02c/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, 
  {'name': "The Wicked Witch", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3eb-05b8-4e45-b3b3-57200ad1e040/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, 
  {'name': 'Durham Performing Arts Center', 'url': 'https://www.dpacnc.com/events/all', 'parser': dpac_parser},
  {'name': 'Carolina Theatre', 'url': 'https://carolinatheatre.org/events/', 'parser': carolina_parser},
  {'name': 'The Rialto', 'url': "https://therialto.com/events/?rhp_bar_rhp_gen=Concerts", 'parser': rhp_parser}, 
  {'name': 'Lincoln Theatre', 'url': 'https://lincolntheatre.com/events/', 'parser': rhp_parser},
  {'name': "The Fruit", 'url': 'https://app.opendate.io/c/durham-fruit-337', 'parser': opendate_parser},
  {'name':"Sharp 9 Gallery Jazz Club", 'url': 'https://clickgobuynow.com/durham/', 'parser': clickgobuynow_parser},
  {'name':"The Ritz Raleigh", 'url': 'https://www.ritzraleigh.com/shows', 'parser': chakra_parser}, 
  {'name':"Duke Arts", 'url': 'https://arts.duke.edu/events/?_series=music-near-the-gardens', 'parser': mrl_parser},
  {'name':"Wake Forest Listening Room", 'url': 'https://wakeforestlisteningroom.com/events/', 'parser': rhp_parser}
  ]

def orange(venue):
  orange_venues = ["Cat's Cradle", "The Cave", "Cat’s Cradle Back Room", "Haw River Ballroom", "Local 506"]
  return venue['venue_name'] in orange_venues

def durham(venue):
  durham_venues = ["Sharp 9 Gallery Jazz Club", "The Fruit", 'Carolina Theatre', 'Durham Performing Arts Center', "Motorco Music Hall", "the Pinhook", "The Pinhook", "Missy Lane's Assembly Room", "Rubies", "Shadowbox Studio", "Duke University East Campus"]
  return venue['venue_name'] in durham_venues

def wake(venue):
  wake_venues = ["The Ritz Raleigh", "The Pour House", "The Night Rider", "The Rialto", "Koka Booth Amphitheatre", "Kings", "Neptunes", "Ruby Deluxe", "Slim's", "The Wicked Witch", "Lincoln Theatre", "Red Hat Amphitheater", "Fletcher Opera Theater", "Memorial Auditorium", "Meymandi Concert Hall", "Kennedy Theater", "Wake Forest Listening Room"]
  return venue['venue_name'] in wake_venues

def dedupe(events_arr):
  print("deduping", len(events_arr), "events")
  working_date = events_arr[0]['human_date']
  working_venue = events_arr[0]['venue_name']
  temp_arr = []
  return_arr = []
  for event in events_arr:
    if (event['venue_name'] != working_venue) or (event['human_date'] != working_date):
      if len(temp_arr) != 2:
        return_arr = return_arr + temp_arr
      else:
        if temp_arr[0]['source'] == temp_arr[1]['source']:
          return_arr = return_arr + temp_arr
        else:
          for temp_event in temp_arr:
            if temp_event['source'] != temp_event['venue_name']:
              return_arr.append(temp_event)
      temp_arr = []
      temp_arr.append(event)
      working_venue = event['venue_name']
      if event['human_date'] != working_date:
        working_date = event['human_date']
    else:
      temp_arr.append(event)
  if len(temp_arr) != 2:
    return_arr = return_arr + temp_arr
  else:
    if temp_arr[0]['source'] == temp_arr[1]['source']:
      return_arr = return_arr + temp_arr
    else:
      for temp_event in temp_arr:
        if temp_event['source'] != temp_event['venue_name']:
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
  durham_sorted = filter(durham, events_deduped)
  orange_sorted = filter(orange, events_deduped)
  wake_sorted = filter(wake, events_deduped)
  today = date.today().strftime('%A, %B %d, %Y')
  template.stream(events=events_deduped, county="all", today=today).dump('index.html')
  template.stream(events=durham_sorted, county="durham", today=today).dump('durham.html')
  template.stream(events=orange_sorted, county="orange", today=today).dump('orange.html')
  template.stream(events=wake_sorted, county="wake", today=today).dump('wake.html')

main()
