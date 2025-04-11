from parsers import rhp_parser
from operator import itemgetter
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template("roksme_index.html")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

venues_list = [{'name':"Cat's Cradle", 'url':'https://catscradle.com/events/?view=list', 'parser':rhp_parser},
  {'name': "Local 506", 'url':'https://local506.com/events/?view=list', 'parser':rhp_parser},
  {'name':"The Pinhook", 'url':'https://thepinhook.com/events/?view=list', 'parser':rhp_parser}]

def main():
  events_array = []
  for venue in venues_list:
    venue_array = venue['parser'](venue['name'], venue['url'], headers)
    events_array = events_array + venue_array
  events_sorted = sorted(events_array, key=itemgetter('event_date'))
  template.stream(events=events_sorted).dump('index.html')

main()
