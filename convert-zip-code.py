#!/usr/bin/env python
# coding: utf-8

from uszipcode import SearchEngine

# Downloads ZIP code data, only call once, not for every search
search = SearchEngine(simple_zipcode = True)

# Search for ZIP code
zipcode = search.by_zipcode("94708")
zipcode = zipcode.to_dict()

# Get county and state
print(zipcode["county"])
print(zipcode["state"])
