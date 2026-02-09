import json
from typing import Dict

mime_types = {
    ".json" : "application/javascript",
    ".html" : "text/html",
    ".css" : "text/css",
    ".gif" : "image/gif",
    ".png" : "image/png",
    ".jpg" : "image/jpeg",
    ".jpeg" : "image/jpeg",
    ".mp4" : "video/mp4",
    ".js" : "text/javascript",
    ".ico" : "image/x-icon",
    ".webp" : "image/webp"
}

class Response:
    def __init__(self):
        self.status_code = 200
        self.status_message = "OK"
        self.headers_dict = {}
        self.cookies_dict = {}
        self.body = b""

    def set_status(self, code : int, text : str):
        self.status_code = code
        self.status_message = text
        return self

    def headers(self, headers):
        self.headers_dict.update(headers)
        return self

    def cookies(self, cookies):
        self.cookies_dict.update(cookies)
        return self

    def bytes(self, data : bytes):
        self.body = self.body + data
        return self

    def text(self, data : str):
        self.body = self.body + data.encode("utf-8")
        return self

    def json(self, data):
        self.headers_dict["Content-Type"] = "application/json"
        jsonstr = json.dumps(data)
        self.body = jsonstr.encode("utf-8")
        return self

    def to_data(self):
        if "Content-Type" not in self.headers_dict:
            self.headers_dict["Content-Type"] = "text/plain; charset=utf-8"
        self.headers_dict["Content-Length"] = str(len(self.body))
        self.headers_dict["X-Content-Type-Options"] = "nosniff"

        head = b"HTTP/1.1" + b" " + str(self.status_code).encode('ascii') + b" " + self.status_message.encode('ascii') + b"\r\n"
        
        for key, value in self.headers_dict.items():
            if key == "Content-Type" or key == "Content-Length":
                continue
            head += key.encode('ascii') + b": " + value.encode('ascii') + b"\r\n"
        if self.cookies_dict:
            head += b"Set-Cookie:"
            for key, value in self.cookies_dict.items():
                head += b" " + key.encode('ascii') + b"=" + value.encode('ascii')
                if len(self.cookies_dict.items()) != 1:
                    head += b";"
            head += b"\r\n"
        head += b"Content-Type: " + self.headers_dict["Content-Type"].encode('ascii') + b"\r\n"
        head += b"Content-Length: " + self.headers_dict["Content-Length"].encode('ascii') + b"\r\n\r\n"

        data = head + self.body

        return data

def send404(handler, message = "File Not Found"):
    res = Response()
    res.set_status(404, "Not Found")
    res.text(message)
    handler.request.sendall(res.to_data())

def send403(handler):
    res = Response()
    res.set_status(403, "Forbidden")
    res.text("You don't have permission to do that")
    handler.request.sendall(res.to_data())

def test1():
    res = Response()
    res.text("hello")
    res.cookies({"session" : "abc123", "testkey" : "testval"})
    print(res.to_data().decode())


if __name__ == '__main__':
    test1()
