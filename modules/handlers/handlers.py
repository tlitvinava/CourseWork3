import os
import re
import json
import uuid
import http.cookies
from urllib.parse import urlparse, parse_qs

from settings import PAGES_DIR
from modules.services.user_service import UserService
from modules.services.coffee_shop_service import CoffeeShopService
from modules.repository.memory_repository import InMemoryRepository


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
        request.send_header('Content-Type', 'application/json; charset=utf-8')
        request.send_header('Access-Control-Allow-Origin', '*')
        request.end_headers()
        request.wfile.write(json.dumps(data).encode('utf-8'))

    @staticmethod
    def get_current_user_or_404(request):
        cookie_header = request.headers.get('Cookie')
        if not cookie_header:
            BaseHandler.respond_json(request, {'success': False, 'message': 'Не авторизован'}, 401)
            return BaseHandler.respond(request, 404, "<h1>404</h1><p>Файл не найден</p>")

        cookies = dict(cookie.split('=') for cookie in cookie_header.split('; ') if '=' in cookie)
        session_id = cookies.get('session_id')
        if not session_id:
            BaseHandler.respond_json(request, {'success': False, 'message': 'Не авторизован'}, 401)
            return BaseHandler.respond(request, 404, "<h1>404</h1><p>Файл не найден</p>")

        mem = InMemoryRepository()
        username = mem.get_username(session_id)
        if not username:
            BaseHandler.respond_json(request, {'success': False, 'message': 'Сессия недействительна'}, 401)
            return BaseHandler.respond(request, 404, "<h1>404</h1><p>Файл не найден</p>")

        us = UserService()

        return us.get_user_by_username(username)

    @staticmethod
    def redirect(request, location):
        request.send_response(302)
        request.send_header('Location', location)
        request.end_headers()


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


class LoginHandler(PathHandlerABC, BaseHandler):
    path = '/login'
    method = "POST"
    context = {}

    @staticmethod
    def handle(request):
        length = int(request.headers.get('Content-Length', 0))
        body = request.rfile.read(length).decode('utf-8')

        try:
            data = json.loads(body)
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        except Exception:
            BaseHandler.respond_json({'success': False, 'message': 'Некорректные данные'}, 400)
            return

        us = UserService()
        err = us.login_user(username, password)
        if err is None:
            BaseHandler.respond_json({'success': False, 'message': "Ошибка авторизации"}, 401)
            return

        session_id = str(uuid.uuid4())

        mem = InMemoryRepository()

        mem.save(session_id, username)

        request.send_response(200)
        request.send_header('Content-Type', 'application/json; charset=utf-8')
        request.send_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
        request.end_headers()
        response = {'success': True, 'message': 'Успешный вход', 'redirect': '/home'}
        request.wfile.write(json.dumps(response).encode('utf-8'))


class RenderHomePage(PathHandlerABC, BaseHandler):
    path = '/home'
    method = "GET"
    context = {}

    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)
        context = {
            'username': user.username,
            'title': 'home'
        }
        BaseHandler.serve_template(request, 'home.html', context)


class AddFavoriteCoffeeShop(PathHandlerABC, BaseHandler):
    path = '/add_favorite'
    method = "POST"

    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)
        if not user:
            return BaseHandler.respond_json(request, {"error": "Не авторизован"}, status=401)

        try:
            length = int(request.headers.get("Content-Length", 0))
            body = request.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            coffee_shop = data.get("coffee_shop")
            if not coffee_shop:
                return BaseHandler.respond_json(request, {"error": "Отсутствует coffee_shop в запросе"}, status=400)

            user_service = UserService()
            added = user_service.add_favorite(user.id, coffee_shop)

            if not added:
                return BaseHandler.respond_json(request, {"error": "Кофейня уже в избранном"}, status=400)

            return BaseHandler.respond_json(request, {"message": "Кофейня добавлена в избранное"})

        except json.JSONDecodeError:
            return BaseHandler.respond_json(request, {"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            print("Ошибка при добавлении кофейни в избранное:", e)
            return BaseHandler.respond_json(request, {"error": str(e)}, status=500)

class RenderFavoriteCoffeeShopsPage(PathHandlerABC, BaseHandler):
    path = '/favorites'
    method = "GET"
    context = {}

    def generate_favorite_list(user):

        coffee_cards = ""
        cs = CoffeeShopService()
        us = UserService()

        for favorite in user.favorites:
            coffee_id = favorite.get("id")
            user_tags = favorite.get("user_tags", [])

            coffee = cs.get_coffee_shop_by_id(coffee_id)
            if not coffee:
                continue

            data = coffee.data
            name = data.get('name', 'Без имени')
            street = data.get('addr:street', '')
            housenumber = data.get('addr:housenumber', '')
            address = f"{street} {housenumber}".strip()

            tags_html = ""
            for tag in user_tags:
                tags_html += f"""
                    <span class='tag'>
                        {tag}
                        <button class='remove-tag-btn' data-tag='{tag}' title='Удалить тег'>×</button>
                    </span>
                """

            coffee_cards += f"""
                <div class='coffee-card' data-coffee-id='{coffee_id}'>
                    <h3>{name}</h3>
                    <p>{address}</p>
                    <div class='tags-list'>{tags_html}</div>
                    <input type='text' class='tag-input' placeholder='Новый тег' />
                    <button class='add-tag-btn'>Добавить тег</button>
                </div>
            """

        return coffee_cards



    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)

        part = RenderFavoriteCoffeeShopsPage.generate_favorite_list(user)

        context = {
            'username': user.username,
            'title': 'Favorites coffeeShops',
            'COFFEESHOPS_GO_HERE': part,
        }
        BaseHandler.serve_template(request, 'favorites_template.html', context)


class AddTagsHandler(PathHandlerABC, BaseHandler):
    path = '/add_tag'
    method = "POST"

    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)
        if not user:
            return BaseHandler.respond_json(request, {"error": "Не авторизован"}, status=401)

        try:
            length = int(request.headers.get("Content-Length", 0))
            body = request.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            coffee_id = int(data.get("coffee_id"))
            tag = data.get("tag", "").strip()

            if not coffee_id or not tag:
                return BaseHandler.respond_json(request, {"error": "Отсутствует coffee_id или tag"}, status=400)

            user_service = UserService()
            success = user_service.add_tag_to_favorite(user.id, coffee_id, tag)

            if not success:
                return BaseHandler.respond_json(request, {"error": "Не удалось добавить тег"}, status=400)

            return BaseHandler.respond_json(request, {"message": "Тег добавлен успешно"})

        except json.JSONDecodeError:
            return BaseHandler.respond_json(request, {"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            print("Ошибка при добавлении тэга:", e)
            return BaseHandler.respond_json(request, {"error": str(e)}, status=500)


class RemoveTagHandler(PathHandlerABC, BaseHandler):
    path = '/remove_tag'
    method = "POST"

    @staticmethod
    def handle(request):
        print("[RemoveTagHandler] Start handle")
        user = BaseHandler.get_current_user_or_404(request)
        print(f"[RemoveTagHandler] User: {user}")
        if not user:
            print("[RemoveTagHandler] Unauthorized user")
            return BaseHandler.respond_json(request, {"error": "Не авторизован"}, status=401)

        try:
            length = int(request.headers.get("Content-Length", 0))
            print(f"[RemoveTagHandler] Content-Length: {length}")
            body = request.rfile.read(length).decode("utf-8")
            print(f"[RemoveTagHandler] Body: {body}")
            data = json.loads(body)

            coffee_id = int(data.get("coffee_id"))
            tag = data.get("tag", "").strip()
            print(f"[RemoveTagHandler] coffee_id={coffee_id}, tag={tag}")

            if not coffee_id or not tag:
                print("[RemoveTagHandler] Missing coffee_id or tag")
                return BaseHandler.respond_json(request, {"error": "Отсутствует coffee_id или tag"}, status=400)

            user_service = UserService()
            success = user_service.remove_tag_from_favorite(user.id, coffee_id, tag)
            print(f"[RemoveTagHandler] remove_tag_from_favorite returned: {success}")

            if not success:
                print("[RemoveTagHandler] Failed to remove tag")
                return BaseHandler.respond_json(request, {"error": "Не удалось удалить тег"}, status=400)

            print("[RemoveTagHandler] Tag removed successfully")
            return BaseHandler.respond_json(request, {"message": "Тег успешно удалён"})

        except json.JSONDecodeError:
            print("[RemoveTagHandler] JSON decode error")
            return BaseHandler.respond_json(request, {"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            print("Ошибка при удалении тэга:", e)
            return BaseHandler.respond_json(request, {"error": str(e)}, status=500)




class GetCoffeShops(PathHandlerABC, BaseHandler):
    path = '/coffee_shops'
    method = "GET"
    context = {}

    staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)
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
        response_data = {
            "results": [service.repository.serializer._to_dict(shop) for shop in results.get("results")],
            "total": total
        }
        BaseHandler.respond_json(request, response_data)


class LogoutHandler(PathHandlerABC, BaseHandler):
    path = '/logout'
    method = "GET"

    @staticmethod
    def handle(request):
        cookie_header = request.headers.get('Cookie')
        if cookie_header:
            cookies = http.cookies.SimpleCookie(cookie_header)
            session_cookie = cookies.get('session_id')
            if session_cookie:
                session_id = session_cookie.value
                mem = InMemoryRepository()
                mem.delete(session_id)

        request.send_response(302)
        request.send_header('Location', '/login')
        request.send_header('Set-Cookie', 'session_id=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/')
        request.end_headers()


class AddFriendHandler(PathHandlerABC, BaseHandler):
    path = '/add_friend'
    method = "POST"

    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)
        if not user:
            return BaseHandler.respond_json(request, {"error": "Не авторизован"}, status=401)

        try:
            length = int(request.headers.get("Content-Length", 0))
            body = request.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            friend_username = data.get("friend_username", "").strip()
            if not friend_username:
                return BaseHandler.respond_json(request, {"error": "Отсутствует friend_username"}, status=400)

            user_service = UserService()

            if not user_service.user_exists(user.username) or not user_service.user_exists(friend_username):
                return BaseHandler.respond_json(request, {"error": "Пользователь не найден"}, status=404)

            added = user_service.add_friend(user.id, friend_username)
            if not added:
                return BaseHandler.respond_json(request, {"message": "Друг уже добавлен"})

            return BaseHandler.respond_json(request, {"message": "Друг добавлен"})

        except json.JSONDecodeError:
            return BaseHandler.respond_json(request, {"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            print("Ошибка при добавлении друга:", e)
            return BaseHandler.respond_json(request, {"error": str(e)}, status=500)


class RenderFriendsPage(PathHandlerABC, BaseHandler):
    path = '/friends'
    method = "GET"
    context = {}

    @staticmethod
    def generate_friends_list(user):
        us = UserService()
        cs = CoffeeShopService()

        friends_data_html = ""

        for friend_username in user.friends:
            friend = us.get_user_by_username(friend_username)
            if not friend:
                continue

            coffee_cards = ""
            for favorite in friend.favorites:
                coffee_id = favorite.get('id')
                user_tags = favorite.get('user_tags', [])

                coffee = cs.get_coffee_shop_by_id(coffee_id)
                if not coffee:
                    continue

                data = coffee.data

                name = data.get('name', 'Без имени')
                street = data.get('addr:street', '')

                tags_html = ''.join(f"<span class='tag'>{tag}</span> " for tag in user_tags)

                coffee_cards += f"""
                <div class='coffee-card' data-coffee-id='{coffee_id}'>
                    <h3>{name}</h3>
                    <p>{street}</p>
                    <div class='tags-list'>{tags_html}</div>
                </div>
                """

            friends_data_html += f"""
            <h2>Друг: {friend.username}</h2>
            {coffee_cards}
            <hr/>
            """

        return friends_data_html

    @staticmethod
    def handle(request):
        user = BaseHandler.get_current_user_or_404(request)

        friends_html = RenderFriendsPage.generate_friends_list(user)

        context = {
            'username': user.username,
            'title': 'Friends',
            'FRIENDS_GO_HERE': friends_html,
        }

        BaseHandler.serve_template(request, 'friends_template.html', context)

