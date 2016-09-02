import argparse
import requests
import sys
import json

from datetime import datetime, timedelta
from geopy.distance import vincenty

from urllib import urlencode

from pprint import pprint

try:
    import config
except ImportError:
    print("Config file config.py.tmpl needs to be copied over to config.py")
    sys.exit(1)

class LagunaTrolley(object):

    def __init__(self, show_all=False):
        self.show_all = show_all

    def busList(self):

        headers = {
            'content-type': 'application/json',
            'X-Parse-Application-Id': config.PARSE_APPLICATION_ID,
            'X-Parse-Client-Key': config.PARSE_CLIENT_KEY
        }

        dtnow = datetime.now().date()
        beginning_of_day = datetime(dtnow.year, dtnow.month, dtnow.day)
        next_day = beginning_of_day + timedelta(1)

        from_str = "%s.000Z" % beginning_of_day.isoformat()
        to_str = "%s.000Z" % next_day.isoformat()

        payload = {
            "_method": "GET",
            "where": {
                "label": {
                    "$regex": "^(?!#11).*$"
                },
                "updatedAt": {
                    "$gte": {
                        "__type": "Date",
                        "iso": from_str
                    },
                    "$lte": {
                        "__type": "Date",
                        "iso": to_str
                    }
                }
            }
        }

        if not self.show_all:
            payload['where']['status'] = "green"

        url = 'https://api.parse.com/1/classes/BusData'
        res = requests.post(url, headers=headers, data=json.dumps(payload))

        data = res.json()

        return data

    def distance(self, latitude, longitude):
        from geopy.distance import vincenty

        from_location = (latitude, longitude)

        bus_data = self.busList()

        print('# of Running Buses: %d' % len(bus_data['results']))
        for idx, bus in enumerate(bus_data['results']):
            bus_location = (bus['point']['latitude'], bus['point']['longitude'])

            miles_distance = vincenty(from_location, bus_location).miles

            bus_name = config.BUS_TAGS.get(bus['bus_id'], bus['bus_id'])
            speed = "average speed %dmph" % bus['avg_speed'] if bus['avg_speed'] > 0 else "stopped"
            print 'Bus [%s] - %s heading %s is %d feet away at "%s"' % (bus_name, speed, bus['compass_heading'], (miles_distance * 5280), bus['address'])

        # pprint(bus_data)

def main():
    parser = argparse.ArgumentParser(prog='lbtrolley')

    parser.add_argument(
        "--lat",
        dest="latitude",
        type=float
    )

    parser.add_argument(
        "--long",
        dest="longitude",
        type=float
    )

    parser.add_argument(
        "--distance",
        dest="distance",
        action="store_true"
    )

    parser.add_argument(
        "--bus_list",
        dest="bus_list",
        action="store_true"
    )

    parser.add_argument(
        "--all",
        dest="all",
        action="store_true"
    )

    args = parser.parse_args()

    lt = LagunaTrolley(show_all=args.all)

    # bus_list = lt.busList()

    if args.distance and args.latitude != None and args.longitude != None:
        lt.distance(args.latitude, args.longitude)
    elif args.bus_list:
        bus_data = lt.busList()
        for bus in bus_data['results']:
            print "Bus ID: %s" % bus['bus_id']
            print "\tAddress: %s" % bus['address']
            print "\tAverage/Instrument Speed: %dmph/%dmph" % (bus['avg_speed'], bus['inst_speed'])
            print "\tHeading: %s" % bus['compass_heading']
            print "\tLat/Long: (%s, %s)" % (bus['point']['latitude'], bus['point']['longitude'])
            print "\tOdometer: %dmi" % bus['odometer']
        # pprint(bus_data)

if __name__ == '__main__':
    main()
