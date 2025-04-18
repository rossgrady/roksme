from parsers import rhp_parser, tribe_parser, tickera_parser, eventprime_parser, ical_parser, mec_parser, avia_parser, sqs_parser, seetickets_parser, freemius_parser, dpac_parser, carolina_parser
from operator import itemgetter
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("roksme_index.html")

venues_list = [{'name':"Cat's Cradle", 'url':'https://catscradle.com/events/?view=list', 'parser':rhp_parser}, {'name': "Local 506", 'url':'https://local506.com/events/?view=list', 'parser':rhp_parser}, {'name':"The Pinhook", 'url':'https://thepinhook.com/events/?view=list', 'parser':rhp_parser}, {'name':"Slim's", 'url':'https://slimsraleigh.com/calendar/list/', 'parser': tribe_parser},{'name':"The Cave", 'url':'https://caverntavern.com/calendar/list/', 'parser': tribe_parser}, {'name':"Motorco", 'url':'https://motorcomusic.com/', 'parser': tickera_parser}, {'name':"Shadowbox Studio", 'url':'https://shadowboxstudio.org/events/', 'parser': mec_parser}, {'name':"Kings", 'url': 'https://www.kingsraleigh.com/', 'parser': eventprime_parser}, {'name': 'Rubies', 'url':'https://rubiesnc.com/', 'parser':avia_parser}, {'name':"Neptunes", 'url': 'https://www.neptunesraleigh.com/events', 'parser': sqs_parser}, {'name':"Missy Lane's Assembly Room", 'url':'https://www.missylanes.com/schedule', 'parser': sqs_parser}, {'name':"The Pour House", 'url': 'https://pourhouseraleigh.com/calendar/', 'parser': seetickets_parser}, {'name': "Ruby Deluxe", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3c2-fa60-4db7-89a5-113d0ad1214d/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, {'name': "The Night Rider", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3da-d7a8-4862-9049-57fd0ad1e02c/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, {'name': "The Wicked Witch", 'url': "https://events.ticketsauce.com/events/events_by_organization/60a71c30-a1e8-48e8-a5b0-1f640ad1e030/662ab3eb-05b8-4e45-b3b3-57200ad1e040/0/0/0/0/false/false/false/true/true/0", 'parser': freemius_parser}, {'name': 'DPAC', 'url': 'https://www.dpacnc.com/events/all', 'parser': dpac_parser},{'name': 'Carolina Theatre', 'url': 'https://carolinatheatre.org/events/', 'parser': carolina_parser}]


def main():
  events_array = []
  for venue in venues_list:
    venue_array = venue['parser'](venue['name'], venue['url'])
    events_array = events_array + venue_array
  events_sorted = sorted(events_array, key=itemgetter('event_date', 'venue_name'))
  template.stream(events=events_sorted).dump('index.html')

main()
