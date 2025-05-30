# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import os
import re
import http.cookies
import uuid
import urllib.parse
from urllib.parse import urlparse, parse_qs
from modules.repository.mongo_repository import MongoRepository
from modules.models.user import User

from modules.services.user_service import UserService
from modules.services.yandex_api_service import YandexAPIService

PORT = 8000

# Инициализация глобального пользовательского сервиса
user_service = UserService()

# Ваш API ключ Яндекс API (замените на настоящий)
YANDEX_API_KEY = "f33e1b69-2a7f-45ca-9397-9ed01c98add7"

'''
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
'''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Папка, где лежит main.py
PAGES_DIR = os.path.join(BASE_DIR, 'views', 'templates')

sessions = {}

users = {
    "admin": "123",
    "user": "qwerty"
}

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def get_current_user(self):
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        cookies = http.cookies.SimpleCookie(cookie_header)
        session_id = cookies.get('session_id')
        if session_id and session_id.value in sessions:
            return sessions[session_id.value]
        return None

    """GET part"""
    def do_GET(self):

        username = self.get_current_user()

        protected_paths = ['/','/index','/home','/favorites']

        if self.path.startswith('/login'):
            self.render_login()
        elif self.path.startswith('/registration'):
            self.render_registration()
        elif self.path == '/logout':
            self.logout()
        elif self.path.startswith('/overpass_coffee_shops'):
                self.get_overpass_coffee_shops()
        elif self.path in protected_paths:
            if username:
                if self.path == '/':
                    self.render_home()
                elif self.path == '/home':
                    self.render_home()
                elif self.path == '/favorites':
                    self.render_favorites_page()
            else:
                self.redirect('/login')
        else:
            self.respond(404, "<h1>404</h1><p>Страница не найдена</p>")

    def render_index(self):
        filepath = os.path.join(PAGES_DIR, 'index.html')
        context = {
            'username': 'Алексей',
            'title': 'Добро пожаловать!'
        }
        self.serve_template(filepath, context)

    def render_home(self):
        filepath = os.path.join(PAGES_DIR, 'home.html')
        context = {
            'username': 'Алексей',
            'title': 'Добро пожаловать!'
        }
        self.serve_template(filepath, context)

    def generate_favorite_list(self, username, favorites):
        filepath = os.path.join(PAGES_DIR, 'favorites_template.html')
        with open(filepath, 'r', encoding='utf-8') as f:
            html_template = f.read()

        coffee_cards = ""
        for coffee in favorites:
            tags = coffee.get('tags', {})
            user_tags = coffee.get('user_tags', [])  # пользовательские теги (список строк)
            name = tags.get('name', 'Без имени')
            street = tags.get('addr:street', '')

            # Формируем HTML для пользовательских тегов
            tags_html = ""
            for tag in user_tags:
                tags_html += f"<span class='tag'>{tag}</span> "

            coffee_cards += f"""
                <div class='coffee-card' data-coffee-id='{coffee.get('id', '')}' data-coffee-type='{coffee.get('type', '')}'>
                    <h3>{name}</h3>
                    <p>{street}</p>
                    <div class='tags-list'>{tags_html}</div>
                    <input type='text' class='tag-input' placeholder='Новый тег' />
                    <button class='add-tag-btn'>Добавить тег</button>
                </div>
                """


        html = html_template.replace("{{COFFEESHOPS_GO_HERE}}", coffee_cards)
        html = html.replace("{{username}}", username)
        return html


    def render_favorites_page(self):
        if not hasattr(self, 'mongo_repo'):
            self.mongo_repo = MongoRepository()

        username = self.get_current_user()
        if not username:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        user = self.mongo_repo.get_user_by_username(username)
        if not user:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "User not found"}')
            return

        favorites = user.favorites  # тут список кофеен из mongo

        # Генерируем html с помощью твоей функции
        html = self.generate_favorite_list(username, favorites)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


    def get_overpass_coffee_shops(self):
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
        url = f"https://overpass-api.de/api/interpreter?data={encoded_query}"

        try:
            with urllib.request.urlopen(url) as response:
                result = json.loads(response.read())
                print(f"Найдено кофеен: {len(result.get('elements', []))}")
                self.respond_json({
                    "message": f"Найдено кофеен: {len(result.get('elements', []))}",
                    "results": result
                })
        except Exception as e:
            print(e)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def render_login(self):
        filepath = os.path.join(PAGES_DIR, 'login.html')
        context = {
            'username': 'Алексей',
            'title': 'Добро пожаловать!'
        }
        self.serve_template(filepath, context)

    def render_registration(self):
        filepath = os.path.join(PAGES_DIR, 'registration.html')
        context = {
            'title': 'Регистрация нового пользователя'
        }
        self.serve_template(filepath, context)

    def serve_template(self, filepath, context):
        try:
            print(os.path.exists(filepath))
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                rendered = self.render_template(content, context)
                self.respond(200, rendered)
        except FileNotFoundError:
            print(FileNotFoundError)
            self.respond(404, "<h1>404</h1><p>Файл не найден</p>")

    def render_template(self, template_str, context):
        def replace_var(match):
            key = match.group(1).strip()
            return str(context.get(key, f'{{{{{key}}}}}'))
        return re.sub(r'\{\{(.*?)\}\}', replace_var, template_str)

    def respond(self, status_code, body):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    """POST part"""
    def do_POST(self):
        if self.path == '/login':
            self.handle_login()
        elif self.path == '/registration':
            self.handle_registration()
        elif self.path == '/coffee_shops':
            self.handle_add_coffee_shop()
        elif self.path == '/add_favorite':
            self.handle_add_favorite()
        elif self.path == '/add_tag':
            self.handle_add_tag()
        else:
            self.respond(404, "<h1>404</h1><p>Страница не найдена</p>")

    def handle_add_tag(self):
        if not hasattr(self, 'mongo_repo'):
            self.mongo_repo = MongoRepository()

        username = self.get_current_user()
        if not username:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            coffee_shop = data.get('coffee_shop')
            tag = data.get('tag')

            if not coffee_shop or not tag:
                raise ValueError("Missing coffee_shop or tag in request body")

            user = self.mongo_repo.get_user_by_username(username)
            if not user:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "User not found"}')
                return

            # Вызываем update_tags с одним тегом
            updated_user = self.mongo_repo.update_tags(user.id, coffee_shop, tag)
            if not updated_user:
                raise ValueError("User or favorite coffee shop not found")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Тег добавлен"}).encode('utf-8'))

        except Exception as e:
            print(e)
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))



    def handle_add_favorite(self):
        if not hasattr(self, 'mongo_repo'):
            self.mongo_repo = MongoRepository()

        username = self.get_current_user()
        if not username:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            coffee_shop = data.get('coffee_shop')
            if not coffee_shop:
                raise ValueError("Missing coffee_shop in request body")

            user = self.mongo_repo.get_user_by_username(username)
            if not user:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "User not found"}')
                return

            # Проверяем, есть ли кофейня уже в избранном
            if coffee_shop in user.favorites:
                message = "Кофейня уже в избранном"
            else:
                self.mongo_repo.add_favorite(user.id, coffee_shop)
                message = "Добавлено в избранное"

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": message}).encode('utf-8'))

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


    def handle_registration(self):
        if not hasattr(self, 'mongo_repo'):
            self.mongo_repo = MongoRepository()
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.respond_json({'success': False, 'message': 'Некорректные данные'}, 400)
            return

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        region = data.get('region', '').strip()

        if not (username and password and phone and email and region):
            self.respond_json({'success': False, 'message': 'Все поля обязательны'}, 400)
            return

        if region.lower() != 'минск':
            self.respond_json({'success': False, 'message': 'В данном регионе приложение не работает'}, 400)
            return

        if self.mongo_repo.get_user_by_username(username) is not None:
            self.respond_json({'success': False, 'message': 'Пользователь с таким именем уже существует'}, 400)
            return

        user = User(username=username, password=password, phone=phone, email=email, region=region)
        self.mongo_repo.add_user(user)

        self.respond_json({'success': True, 'message': 'Регистрация прошла успешно', 'redirect': '/login'})

    def handle_login(self):
        if not hasattr(self, 'mongo_repo'):
            self.mongo_repo = MongoRepository()
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.respond_json({'success': False, 'message': 'Некорректные данные'}, 400)
            return

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        user = self.mongo_repo.get_user_by_username(username)
        if user is None or user.password != password:
            self.respond_json({'success': False, 'message': 'Неверный логин или пароль'}, 401)
            return

        session_id = str(uuid.uuid4())
        sessions[session_id] = username
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
        self.end_headers()
        response = {'success': True, 'message': 'Успешный вход', 'redirect': '/'}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_add_coffee_shop(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.respond_json({'success': False, 'message': 'Некорректные данные'}, 400)
            return

        # Проверяем обязательные поля
        name = data.get('name')
        address = data.get('address')
        if not name or not address:
            self.respond_json({'success': False, 'message': 'Необходимо указать название и адрес'}, 400)
            return

        price = data.get('price', '')
        wifi = data.get('wifi', '')

        # Пример объекта кофейни
        coffee_shop = {
            'name': name,
            'address': address,
            'price': price,
            'wifi': wifi
        }

        try:
            # Если у тебя есть репозиторий, то вызывай метод сохранения, например:
            self.mongo_repo.add_coffee_shop(coffee_shop)
            # Если репозитория нет, можно добавить в глобальный список или аналог
            # coffee_shops.append(coffee_shop)
        except Exception as e:
            self.respond_json({'success': False, 'message': f'Ошибка при сохранении: {str(e)}'}, 500)
            return

        self.respond_json({'success': True, 'message': 'Кофейня добавлена', 'coffee_shop': coffee_shop}, 201)


    def respond_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')  # Разрешаем кросс-доменные запросы
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def logout(self):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookies = http.cookies.SimpleCookie(cookie_header)
            session_id = cookies.get('session_id')
            if session_id and session_id.value in sessions:
                del sessions[session_id.value]
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'session_id=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/')
        self.end_headers()

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
