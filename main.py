# -*- coding: utf-8 -*-
import http.server
import socketserver
import json

# Импортируем сервис пользователей
from modules.services.user_service import UserService

PORT = 8000

# Глобальный объект UserService с in-memory репозиторием
user_service = UserService()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            message = (
                "<html>"
                "<head><title>Кофейни Минска</title></head>"
                "<body>"
                "<h1>Добро пожаловать на платформу поиска кофеен!</h1>"
                "<p>Используйте POST /register для регистрации пользователя.</p>"
                "</body>"
                "</html>"
            )
            self.wfile.write(message.encode("utf-8"))
        else:
            self.send_error(404, "Страница не найдена")

    def do_POST(self):
        if self.path == "/register":
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                #self.wfile.write(b"Неверный формат JSON")
                return

            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                self.send_response(400)
                self.end_headers()
                #self.wfile.write(b"Необходимо указать 'username' и 'password'")
                return

            try:
                new_user = user_service.register_user(username, password)
            except ValueError as ve:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(ve).encode("utf-8"))
                return

            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            response = new_user.to_dict()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            #self.wfile.write(b"Неизвестный endpoint")

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
