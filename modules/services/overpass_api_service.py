import json
import urllib.parse
import urllib.request

import json
import urllib.parse
import urllib.request

class OverpassAPIService:
    endpoint = "https://overpass-api.de/api/interpreter?data="

    @staticmethod
    def get_overpass_coffee_shops():
        query = """
        [out:json];
        (
        node["amenity"~"cafe|restaurant|fast_food"](around:9000,53.9,27.56667);
        way["amenity"~"cafe|restaurant|fast_food"](around:9000,53.9,27.56667);
        node["shop"="coffee"](around:9000,53.9,27.56667);
        way["shop"="coffee"](around:9000,53.9,27.56667);
        );
        out center;
        """
        encoded_query = urllib.parse.quote(query)
        url = f"{OverpassAPIService.endpoint}{encoded_query}"

        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read())
            print(f"Найдено кофеен: {len(result.get('elements', []))}")
            return {
                "message": f"Найдено кофеен: {len(result.get('elements', []))}",
                "results": result
            }
