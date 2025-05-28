# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import os
import math

# Импорт сервисов
from modules.services.user_service import UserService
from modules.services.coffee_shop_service import CoffeeShopService

PORT = 8000

# Глобальные объекты сервисов
user_service = UserService()
coffee_shop_service = CoffeeShopService()

# Для демонстрации — предопределённая кофейня для отправки уведомления
NOTIFICATION_COFFEE_SHOP = {
    "name": "Coffee House",
    "latitude": 53.9,
    "longitude": 27.56667
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками (в километрах)
    по формуле Хаверсайна.
    """
    R = 6371  # Радиус Земли в км
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            # Отдаем HTML-страницу
            try:
                with open("views/templates/index.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Ошибка загрузки страницы index.html".encode("utf-8"))
        elif self.path == "/coffee_shops":
            # Эндпоинт для получения списка кофеен
            shops = coffee_shop_service.list_coffee_shops()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            response = json.dumps(shops, ensure_ascii=False)
            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Страница не найдена".encode("utf-8"))
    
    def do_POST(self):
        try:
            if self.path == "/register":
                # Регистрация пользователя
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Неверный формат JSON".encode("utf-8"))
                    return
                username = data.get("username")
                password = data.get("password")
                if not username or not password:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Необходимо указать 'username' и 'password'".encode("utf-8"))
                    return
                try:
                    new_user = user_service.register_user(username, password)
                except ValueError as ve:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(str(ve).encode("utf-8"))
                    return
                self.send_response(201)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(new_user.to_dict(), ensure_ascii=False).encode("utf-8"))
            
            elif self.path == "/coffee_shops":
                # Создание новой кофейни
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Неверный формат JSON".encode("utf-8"))
                    return
                name = data.get("name")
                address = data.get("address")
                if not name or not address:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Необходимо указать 'name' и 'address'".encode("utf-8"))
                    return
                attributes = {key: value for key, value in data.items() if key not in ["name", "address"]}
                new_shop = coffee_shop_service.create_coffee_shop(name, address, **attributes)
                self.send_response(201)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(new_shop.to_dict(), ensure_ascii=False).encode("utf-8"))
            
            elif self.path == "/update_location":
                # Обновление геолокации пользователя и отправка уведомления.
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Неверный формат JSON".encode("utf-8"))
                    return
                try:
                    latitude = float(data.get("latitude"))
                    longitude = float(data.get("longitude"))
                except (TypeError, ValueError):
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("Неверные координаты".encode("utf-8"))
                    return

                # Расчет расстояния до предопределенной кофейни
                distance = haversine_distance(latitude, longitude,
                                              NOTIFICATION_COFFEE_SHOP["latitude"],
                                              NOTIFICATION_COFFEE_SHOP["longitude"])
                if distance < 0.1:  # если расстояние менее 100 метров
                    notification = f"Вы находитесь недалеко от {NOTIFICATION_COFFEE_SHOP['name']}. Хотите оценить сервис?"
                else:
                    notification = "На данный момент уведомлений нет."
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                response = {"notification": notification, "distance_km": distance}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Неизвестный endpoint".encode("utf-8"))
        except Exception as ex:
            print("Ошибка обработки запроса:", ex)
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Внутренняя ошибка сервера".encode("utf-8"))

def run_server():
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print("Сервер запущен на порту {}...".format(PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Сервер остановлен")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
