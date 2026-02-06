import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
import util.file_routes
import util.chat

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        self.router.add_route("GET", "/public", util.file_routes.get_file, False)
        self.router.add_route("GET", "/", util.file_routes.render_html, True)
        self.router.add_route("GET", "/chat", util.file_routes.render_html, True)
        self.router.add_route("POST", "/api/chats", util.chat.create_message, True)
        self.router.add_route("GET", "/api/chats", util.chat.get_messages, True)
        self.router.add_route("PATCH", "/api/chats/", util.chat.update_message, False)
        self.router.add_route("DELETE", "/api/chats/", util.chat.delete_message, False)
        self.router.add_route("PATCH", "/api/reaction/", util.chat.add_reaction, False)
        self.router.add_route("DELETE", "/api/reaction/", util.chat.remove_reaction, False)
        self.router.add_route("PATCH", "/api/nickname", util.chat.edit_nickname, True)
        self.router.add_route("GET", "/change-avatar", util.file_routes.render_html, True)
        self.router.add_route("GET", "/change-avatar", util.file_routes.render_html, True)
        self.router.add_route("GET", "/chat", util.file_routes.render_html, True)
        self.router.add_route("GET", "/direct-messaging", util.file_routes.render_html, True)
        self.router.add_route("GET", "/drawing-board", util.file_routes.render_html, True)
        self.router.add_route("GET", "/index", util.file_routes.render_html, True)
        self.router.add_route("GET", "/register", util.file_routes.render_html, True)
        self.router.add_route("GET", "/login", util.file_routes.render_html, True)
        self.router.add_route("GET", "/search-users", util.file_routes.render_html, True)
        self.router.add_route("GET", "/set-thumbnail", util.file_routes.render_html, True)
        self.router.add_route("GET", "/settings", util.file_routes.render_html, True)
        self.router.add_route("GET", "/test-websocket", util.file_routes.render_html, True)
        self.router.add_route("GET", "/upload", util.file_routes.render_html, True)
        self.router.add_route("GET", "/video-call-room", util.file_routes.render_html, True)
        self.router.add_route("GET", "/video-call", util.file_routes.render_html, True)
        self.router.add_route("GET", "/videotube", util.file_routes.render_html, True)
        self.router.add_route("GET", "/view-video", util.file_routes.render_html, True)
        # TODO: Add your routes here
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
