# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs

from modules.services.user_service import UserService
from modules.services.yandex_api_service import YandexAPIService

PORT = 8000

# Инициализация глобального пользовательского сервиса
user_service = UserService()

# Ваш API ключ Яндекс API (замените на настоящий)
YANDEX_API_KEY = "f33e1b69-2a7f-45ca-9397-9ed01c98add7"

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def serve_file(self, filename, content_type="text/html; charset=utf-8"):
        try:
            with open(filename, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Ошибка загрузки файла {}: {}".format(filename, e).encode("utf-8"))

    def do_GET(self):
        if self.path.startswith("/yandex_coffee_shops"):
            # Создаем экземпляр сервиса для работы с Яндекс API
            yandex_service = YandexAPIService(YANDEX_API_KEY)
            # Разбираем URL, чтобы извлечь параметры запроса
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            # Извлекаем значение параметра "query". Если его нет – используем значение по умолчанию "кофейня"
            query_text = qs.get("query", ["кофейня"])[0]
        try:
            # Выполняем поиск, передавая извлеченный запрос
            data = yandex_service.search_coffee_shops(query=query_text)
            features = data.get("features", [])
            if features:
                # Формируем список найденных названий кофеен
                names = [
                    feature.get("properties", {}).get("name", "Без названия")
                    for feature in features
                ]
                message = "Найдены кофейни: " + ", ".join(names)
            else:
                message = "Кофейня не найдена для запроса: " + query_text
            response_obj = {"message": message, "results": data}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_obj, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Ошибка получения данных от Яндекс API: {}".format(e).encode("utf-8"))
    # Обработка других GET-запросов (например, регистрация, вход, домашняя страница)...

    def do_POST(self):
        # Чтение тела запроса (ожидается формат JSON)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Неверный формат JSON".encode("utf-8"))
            return

        if self.path == "/registration":
            username = data.get("username")
            password = data.get("password")
            phone    = data.get("phone")
            email    = data.get("email")
            region   = data.get("region")
            if not (username and password and phone and email and region):
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Все поля обязательны".encode("utf-8"))
                return
            if region.lower() != "минск":
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("В данном регионе приложение не работает".encode("utf-8"))
                return
            try:
                new_user = user_service.register_user(username, password, phone, email, region)
            except ValueError as ve:
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(str(ve).encode("utf-8"))
                return
            response_obj = {"message": "Регистрация прошла успешно", "redirect": "/home"}
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_obj, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/login":
            username = data.get("username")
            password = data.get("password")
            if not (username and password):
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Необходимо указать username и password".encode("utf-8"))
                return
            user = user_service.login_user(username, password)
            if not user:
                self.send_response(401)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Неверное имя пользователя или пароль".encode("utf-8"))
                return
            response_obj = {"message": "Вход выполнен успешно", "redirect": "/home"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_obj, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Неизвестный endpoint".encode("utf-8"))

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
