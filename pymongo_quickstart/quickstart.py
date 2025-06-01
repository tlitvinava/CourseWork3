from modules.services.coffee_shop_service import CoffeeShopService
from modules.services.overpass_api_service import OverpassAPIService
from modules.models.coffeeshop import CoffeeShop

def get_actual_mongo_data():
    result_from_api = OverpassAPIService.get_overpass_coffee_shops().get("results")
    cs = CoffeeShopService()

    for cofe in result_from_api['elements']:
        new_cofe = CoffeeShop(cofe.get('id',None), cofe.get('lat',None), cofe.get('lon',None), cofe.get('tags', None))
        cs.add_or_update_coffee_shop(new_cofe)