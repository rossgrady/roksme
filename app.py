from parsers import rhp_parser, tribe_parser, tickera_parser, ical_parser, mec_parser
from operator import itemgetter
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("roksme_index.html")

venues_list = [{'name':"Cat's Cradle", 'url':'https://catscradle.com/events/?view=list', 'parser':rhp_parser}, {'name': "Local 506", 'url':'https://local506.com/events/?view=list', 'parser':rhp_parser}, {'name':"The Pinhook", 'url':'https://thepinhook.com/events/?view=list', 'parser':rhp_parser}, {'name':"Slim's", 'url':'https://slimsraleigh.com/calendar/list/', 'parser': tribe_parser},{'name':"The Cave", 'url':'https://caverntavern.com/calendar/list/', 'parser': tribe_parser}, {'name':"Motorco", 'url':'https://motorcomusic.com/', 'parser': tickera_parser}, {'name':"Shadowbox Studio", 'url':'https://shadowboxstudio.org/events/', 'parser': mec_parser}]

def main():
  events_array = []
  for venue in venues_list:
    venue_array = venue['parser'](venue['name'], venue['url'])
    events_array = events_array + venue_array
  events_sorted = sorted(events_array, key=itemgetter('event_date', 'venue_name'))
  template.stream(events=events_sorted).dump('index.html')

main()
