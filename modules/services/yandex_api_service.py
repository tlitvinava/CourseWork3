# -*- coding: utf-8 -*-
import requests

class YandexAPIService:
    def __init__(self, api_key):
        self.api_key = api_key
        # URL для поиска организаций через Яндекс.Карты
        self.endpoint = "https://search-maps.yandex.ru/v1/"

    def search_coffee_shops(self, query="кофейня", ll="27.56667,53.9", results=10, lang="ru_RU"):
        """
        Выполняет поиск организаций по запросу.
        
        Параметры:
          query  – поисковый запрос (например, 'кофейня')
          ll     – координаты центра поиска в формате "долгота,широта" (например, центр Минска)
          results – количество возвращаемых результатов
          lang   – язык результатов (по умолчанию ru_RU)
          
        Возвращает JSON с данными полученных организаций.
        """
        params = {
            "apikey": self.api_key,
            "text": query,
            "lang": lang,
            "ll": ll,
            "type": "biz",  # ищем организации
            "results": results
        }
        response = requests.get(self.endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

# Пример использования:
if __name__ == "__main__":
    API_KEY = "f33e1b69-2a7f-45ca-9397-9ed01c98add7"
    yandex_service = YandexAPIService(API_KEY)
    try:
        data = yandex_service.search_coffee_shops()
        print("Результаты поиска организаций:")
        print(data)
    except Exception as e:
        print("Ошибка при запросе к Яндекс API:", e)
