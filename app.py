import argparse
import requests
import sys
import json

import datetime

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
                        "iso": "2016-09-02T00:00:00.000Z"
                    },
                    "$lte": {
                        "__type": "Date",
                        "iso": "2016-09-03T00:00:00.000Z"
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

    parser.add_argument(
        "--test",
        dest="test",
        action="store_true"
    )

    args = parser.parse_args()

    lt = LagunaTrolley()

    lt.busList()

if __name__ == '__main__':
    main()
