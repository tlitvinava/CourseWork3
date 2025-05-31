# -*- coding: utf-8 -*-
import uuid

class CoffeeShop:
    def __init__(self, id , lat, lon, data, **attributes):
        self.id = id if id is not None else str(uuid.uuid4())
        self.lat = lat
        self.lon = lon
        self.data = data

