# -*- coding: utf-8 -*-
import uuid

class CoffeeShop:

    __non_recursive_fields__ = ["data"]

    def __init__(self, id , lat, lon, data, **attributes):
        self.id = id if id is not None else str(uuid.uuid4())
        self.lat = lat
        self.lon = lon
        self.data = data

