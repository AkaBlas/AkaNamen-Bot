#!/usr/bin/env python
import json
from tests.check_file_path import check_file_path
from copy import deepcopy
from geopy import Location, Point

with open(check_file_path('tests/data/addresses.txt'), 'r') as file:
    ADDRESSES = json.loads(file.read())


def get_address_from_cache(*args):
    if len(args) == 1:
        address = args[0]
    else:
        address = args[1]

    # deepcopy here for cases were we fiddle with the data
    # eg in TestMember::test_set_address_bad_response
    # Maybe shallow copy will do, but better be sure …
    address = deepcopy(ADDRESSES.get(address))

    if address is None:
        return None
    if not isinstance(address['point'], Point):
        address['point'] = Point(**address['point'])
    return Location(**address)
