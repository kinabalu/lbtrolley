import argparse
import requests
import sys
import json

from datetime import datetime, timedelta

from urllib import urlencode

from pprint import pprint

try:
    import config
except ImportError:
    print("Config file config.py.tmpl needs to be copied over to config.py")
    sys.exit(1)

class LagunaTrolley(object):

    def __init__(self):
        pass

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
                "status": "green",
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

        url = 'https://api.parse.com/1/classes/BusData'
        res = requests.post(url, headers=headers, data=json.dumps(payload))

        data = res.json()

        pprint(data)


def main():
    parser = argparse.ArgumentParser(prog='lbtrolley')

    # parser.add_argument(
    #     "--test",
    #     dest="test",
    #     action="store_true"
    # )

    args = parser.parse_args()

    lt = LagunaTrolley()

    lt.busList()

if __name__ == '__main__':
    main()
