# coding: utf-8
from __future__ import print_function

import os
import re
import sys
import time

import requests
from flowdock import TeamInbox

FLOWDOCK_API_KEY = os.environ.get('FLOWDOCK_API_KEY')
COFFEE_URL = os.environ.get('COFFEE_URL', 'http://192.168.179.80:8080/')
USE_SAMPLE_DATA = bool(int(os.environ.get('USE_SAMPLE_DATA', 1)))

def normalize(x):
    return min(1, float(x) / 100)

if not FLOWDOCK_API_KEY:
    print('FLOWDOCK_API_KEY not set, using simulated team box...')
    class DummyTeamInbox(object):
        def post(self, *args, **kwargs):
            print('POST:', args, kwargs)
    inbox = DummyTeamInbox()
else:
    inbox = TeamInbox(FLOWDOCK_API_KEY)

SAMPLE_ROWS = open('sample_data.txt').readlines()
if USE_SAMPLE_DATA:
    print('Using sample data...')

COFFEE_NO = 0
COFFEE_COMING = 1
COFFEE_READY = 2

incoming_coffee = COFFEE_NO
coffee_level = 0.0
i = 4
while True:
    i += 1
    if USE_SAMPLE_DATA:
        coffee_levels = list(map(normalize, [int(x.strip()) for x in SAMPLE_ROWS]))[0:i]
        if i >= len(SAMPLE_ROWS):
            sys.exit(0)
    else:
        req = requests.get(COFFEE_URL)
        coffee_levels = [
            normalize(int(x)) for x in re.findall('([0-9]+)<', req.content.decode('utf-8'))
        ]

    now = coffee_levels[-1]
    diff1 = coffee_levels[-1] - coffee_levels[-2]
    diff2 = coffee_levels[-2] - coffee_levels[-3]

    print(i, now, diff1, diff2)
    if diff1 >= 0.05 and diff2 >= 0.05:
        incoming_coffee = COFFEE_COMING
    elif incoming_coffee == COFFEE_COMING and abs(diff1) < 0.05:
        coffee_level = now
        incoming_coffee = COFFEE_READY
        cups_of_coffee = int(round(now * 10))
        inbox.post(
            'Barista',
            'teemu+barista@fastmonkeys.com',
            'Coffee is ready!',
            '<p>%s</p>' % ('☕ ' * cups_of_coffee),
            tags='@team'
        )
    elif incoming_coffee == COFFEE_READY and now <= 0.1:
        incoming_coffee = COFFEE_NO
        inbox.post(
            'Barista',
            'teemu+barista@fastmonkeys.com',
            'Out of coffee',
            '<p></p>'
        )
    elif (
        incoming_coffee == COFFEE_READY and
        abs(diff1) < 0.05 and
        diff2 < -0.05 and
        (coffee_level-now) > 0.05
    ):
        coffee_level = now
        cups_of_coffee = int(round(now * 10))
        inbox.post(
            'Barista',
            'teemu+barista@fastmonkeys.com',
            'Coffee is consumed',
            '<p>%s</p>' % ('☕ ' * cups_of_coffee)
        )

    if USE_SAMPLE_DATA:
        time.sleep(0.05)
    else:
        time.sleep(2)
