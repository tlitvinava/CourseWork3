# -*- coding: utf-8 -*-
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

from modules.handlers.handlers import PathHandlerABC
from pymongo_quickstart.quickstart import get_actual_mongo_data

PORT = 8000

class RequestHandler(http.server.BaseHTTPRequestHandler):

    post_paths: dict[str, callable] = {}
    get_paths: dict[str, callable] = {}

    """GET part"""
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_only = parsed_path.path

        print(self.path)
        g = PathHandlerABC.get_handlers.get(path_only, None)
        print(g)
        if g is None:
            return 404
        g.handle(request=self)

    """POST part"""
    def do_POST(self):
        print(self.path)
        p = PathHandlerABC.post_handlers.get(self.path, None)
        print(p)
        if p is None:
            return 404
        p.handle(request=self)

def run_server():
    #get_actual_mongo_data()
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print("Сервер запущен на порту {}...".format(PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Сервер остановлен")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
