import base64


VALID_USERNAME = 'admin'
VALID_PASSWORD = 'momo2024'


def check_auth(handler):
    auth_header = handler.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        _reject(handler)
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
        username, password = decoded.split(':', 1)
    except Exception:
        _reject(handler)
        return False
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return True
    _reject(handler)
    return False


def _reject(handler):
    body = b'{"error": "Unauthorized"}'
    handler.send_response(401)
    handler.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(body)