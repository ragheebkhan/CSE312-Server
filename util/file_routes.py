import util.request
import util.response
from pathlib import Path

def verify_public_file(request_path):
    public_dir = Path(__file__).resolve().parent.parent / "public"

    req_path = Path(request_path.replace("/public/", ""))
    req_path = public_dir / req_path
    req_path = req_path.resolve()

    in_public = False

    for path in public_dir.rglob('*'):
        if path == req_path:
            in_public = True
            break
    
    if not in_public:
        return None
    return req_path


def get_file(request : util.request.Request, handler):

    req_path = verify_public_file(request.path)

    if req_path == None:
        util.response.send404(handler)

    res = util.response.Response()

    mime_type = util.response.mime_types[req_path.suffix.lower()]

    file_bytes = b""

    with open(req_path, 'rb') as file:
        file_bytes = file.read()

    
    res.headers({"Content-Type" : mime_type})
    res.bytes(file_bytes)

    print(res.to_data())
    handler.request.sendall(res.to_data())

def render_html(request : util.request.Request, handler):

    layout_path = Path(__file__).parent.parent / "public" / "layout" / "layout.html"
    layout_content = b""

    with open(layout_path, 'rb') as file:
        layout_content = file.read()

    file_content = b""

    if request.path == "/":
        filepath = layout_path.parent.parent / "index.html"
    else:
        filepath = layout_path.parent.parent / (request.path.replace("/","") + ".html")
    
    with open(filepath, 'rb') as file:
        file_content = file.read()
    
    layout_content.replace(b"{{content}}", file_content)

    res = util.response.Response()

    res.headers({"Content-Type" : util.response.mime_types[".html"]})
    res.bytes(layout_content.replace(b"{{content}}", file_content))

    print(res.to_data())

    handler.request.sendall(res.to_data())







    