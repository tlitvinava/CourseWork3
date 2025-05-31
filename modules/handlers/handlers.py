import os
import re
import json
from urllib.parse import urlparse, parse_qs

from settings import PAGES_DIR
from modules.services.user_service import UserService
from modules.services.coffee_shop_service import CoffeeShopService


class PathHandlerABC():
    post_handlers = {}
    get_handlers = {}

    def __init_subclass__(cls):
        if cls.method == "GET":
            PathHandlerABC.get_handlers[cls.path] = cls
        elif cls.method == "POST":
            PathHandlerABC.post_handlers[cls.path] = cls


class BaseHandler():

    @staticmethod
    def render_template(template_str, context):
        def replace_var(match):
            key = match.group(1).strip()
            return str(context.get(key, f'{{{{{key}}}}}'))
        return re.sub(r'\{\{(.*?)\}\}', replace_var, template_str)

    @staticmethod
    def serve_template(request, filename, context=None, status_code=200):
        if context is None:
            context = {}
        filepath = os.path.join(PAGES_DIR, filename)
        print(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            rendered = BaseHandler.render_template(content, context)
            BaseHandler.respond(request, status_code, rendered)
        except FileNotFoundError:
            BaseHandler.respond(request, 404, "<h1>404</h1><p>Файл не найден</p>")

    @staticmethod
    def respond(request, status_code, body, content_type='text/html; charset=utf-8'):
        request.send_response(status_code)
        request.send_header('Content-type', content_type)
        request.end_headers()
        request.wfile.write(body.encode('utf-8'))

    @staticmethod
    def respond_json(request, data, status=200):
        request.send_response(status)
        request.send_header("Content-Encoding", "UTF-8")
        request.send_header('Content-Type', 'application/json; charset=utf-8')
        request.send_header('Access-Control-Allow-Origin', '*')
        request.end_headers()
        request.wfile.write(json.dumps(data).encode('utf-8'))


class RenderRegistrstionPage(PathHandlerABC, BaseHandler):
    path = '/registration'
    method = "GET"
    context = {}

    @staticmethod
    def handle(request):
        context = {
            'title': 'Registration'
        }
        BaseHandler.serve_template(request, 'registration.html', context)

class RegistrationHandler(PathHandlerABC, BaseHandler):
    path = '/registration'
    method = "POST"
    context = {}

    @staticmethod
    def handle(request):
        length = int(request.headers.get('Content-Length', 0))
        body = request.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            request.respond_json({'success': False, 'message': 'Некорректные данные'}, 400)
            return
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        region = data.get('region', '').strip()
        us = UserService()
        try:
            us.register_user(username, password, phone, email, region)
        except ValueError as e:
            print(e)
            BaseHandler.respond_json(request, {'success': False, 'message': str(e)}, 400)
            return
        BaseHandler.respond_json(request, {'success': True, 'message': 'Регистрация прошла успешно', 'redirect': '/login'})

class RenderLoginPage(PathHandlerABC, BaseHandler):
    path = '/login'
    method = "GET"
    context = {}

    @staticmethod
    def handle(request):
        context = {
            'title': 'LogIn'
        }
        BaseHandler.serve_template(request, 'login.html', context)


class RenderHomePage(PathHandlerABC, BaseHandler):
    path = '/home'
    method = "GET"
    context = {}

    @staticmethod
    def handle(request):
        context = {
            'username': 'User',
            'title': 'home'
        }
        BaseHandler.serve_template(request, 'home.html', context)

class RenderFavoriteCoffeeShopsPage(PathHandlerABC, BaseHandler):
    path = '/favorites'
    method = "GET"
    context = {}

    def generate_favorite_list(user_id):

        coffee_cards = ""
        for coffee in []:
            tags = coffee.get('tags', {})
            user_tags = coffee.get('user_tags', [])
            name = tags.get('name', 'Без имени')
            street = tags.get('addr:street', '')


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

        return coffee_cards

    @staticmethod
    def handle(request):
        context = {
            'username': 'User',
            'title': 'home',
        }
        BaseHandler.serve_template(request, 'home.html', context)


class GetCoffeShops(PathHandlerABC, BaseHandler):
    path = '/coffee_shops'
    method = "GET"
    context = {}

    staticmethod
    def handle(request):
        print(request)
        parsed_url = urlparse(request.path)
        params = parse_qs(parsed_url.query)

        page = int(params.get('page', ['1'])[0])
        per_page = int(params.get('per_page', ['10'])[0])
        query = params.get('query', [''])[0]
        print(page, per_page, query)
        service = CoffeeShopService()
        results = service.get_shops(page=page, per_page=per_page, query=query)
        total = results.get('total')
        print(results)
        response_data = {
            "results": [service.repository.serializer._to_dict(shop) for shop in results.get("results")],
            "total": total
        }
        print(response_data)
        BaseHandler.respond_json(request, response_data)