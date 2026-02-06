class Request:

    def __init__(self, request: bytes):
        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        head, body = self.split_request(request)

        self.body = body

        self.method, self.path, self.http_version, self.headers, self.cookies = self.parse_head(head)


    def split_request(self, request : bytes):
        blank_line_idx = request.find(b"\r\n\r\n")
        return (request[:blank_line_idx].decode('ascii'), request[blank_line_idx + 4:])
    
    def parse_head(self, head : str):
        split_head = head.splitlines()

        split_request_line = split_head[0].split(" ")

        method = split_request_line[0]
        path = split_request_line[1]
        version = split_request_line[2]

        if len(split_head) == 1:
            return (method, path, version, {}, {})
        
        headers = self.parse_headers(split_head[1:])
        cookies = self.parse_cookies(headers)

        return (method, path, version, headers, cookies)
        
    def parse_headers(self, headers):
        headers_dict = {}
        for line in headers:
            colon_idx = line.find(":")
            if(colon_idx == -1):
                continue
            key = line[:colon_idx]
            value = line[colon_idx + 1 :]
            key = key.strip()
            value = value.strip()
            headers_dict[key] = value
        return headers_dict
    
    def parse_cookies(self, headers_dict):
        cookies_dict = {}
        cookie_key = ""

        for key in headers_dict.keys():
            if key.lower() != "cookie":
                continue
            cookie_key = key
            break

        if cookie_key == "":
            return {}
        
        cookie_line = headers_dict[cookie_key]

        kv_pairs = cookie_line.split(";")

        for pair in kv_pairs:
            pair_stripped = pair.replace(" ","")
            if pair_stripped == "":
                continue
            pair_split = pair_stripped.split("=")
            cookies_dict[pair_split[0].strip()] = pair_split[1].strip()

        return cookies_dict

def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: testkey=testvalue\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert "Cookie" in request.headers
    assert "testkey" in request.cookies
    assert request.cookies["testkey"] == "testvalue"
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct

if __name__ == '__main__':
    test1()
