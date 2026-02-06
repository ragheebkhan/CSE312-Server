from util.response import send404

class Route:
    def __init__(self, method, path, action, exact_path):
        self.method = method
        self.path = path
        self.action = action
        self.exact_path = exact_path

    def is_match(self, request):
        if self.exact_path:
            return self.method ==  request.method and self.path == request.path
        else:
            return (self.method ==  request.method and self.path == request.path) or (self.method == request.method and request.path.startswith(self.path))

class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        route = Route(method, path, action, exact_path)
        self.routes.append(route)

    def route_request(self, request, handler):
        for route in self.routes:
            if route.is_match(request):
                route.action(request, handler)
                return
        send404(handler)
