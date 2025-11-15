"""
Test utilities for creating WSGI fixtures for testing HTTP clients.
"""

import contextlib
from http import client
import io
import json
import multiprocessing
from wsgiref.simple_server import make_server


def start_server(app, queue, returns_app):
    """
    Run a fixture application.
    """
    # 'app' is actually a callable that returns an app. Useful when dealing
    # with a app implemented as a class.
    if returns_app:
        app = app()
    svr = make_server("localhost", 0, app)
    queue.put(("localhost", svr.server_port))
    svr.serve_forever()


@contextlib.contextmanager
def fixture(app, *, returns_app=False):
    """
    Start the given application fixture in its own process, yielding a socket
    connected to it.

    Set `returns_app` if `app` is a callable that returns the actual app (such
    as a class).
    """
    queue = multiprocessing.Queue()

    # Spin up a separate process for our fixture server.
    proc = multiprocessing.Process(target=start_server, args=(app, queue, returns_app))
    proc.start()
    if proc.exitcode is not None:  # pragma: no cover
        raise RuntimeError(f"{app} didn't start")

    try:
        hostname, port = queue.get(timeout=5)
        yield f"http://{hostname}:{port}/"
    finally:
        if proc.exitcode is None:
            proc.terminate()
        queue.close()


def get_content_length(environ):
    content_length = environ.get("CONTENT_LENGTH", None)
    return None if content_length is None else int(content_length)


def read_body(environ):
    return environ["wsgi.input"].read(get_content_length(environ))


def read_json(environ):
    if environ["CONTENT_TYPE"] == "application/json":
        return json.loads(read_body(environ))
    return None


def extract_environment(environ):
    non_http = [
        "CONTENT_LENGTH",
        "CONTENT_TYPE",
        "PATH_INFO",
        "QUERY_STRING",
        "REQUEST_METHOD",
    ]
    return {key: value for key, value in environ.items() if key in non_http or key.startswith("HTTP_")}


def _al_contains(al, key):
    """
    Treating `al` as an association list (a list of two-tuples), return `True`
    if `key` is a key value.
    """
    return any(k == key for k, _ in al)


def response(start_response, code, body="", headers=None):
    if headers is None:
        headers = []
    headers.append(("Content-Length", str(len(body))))
    start_response(f"{code} {client.responses[code]}", headers)
    return [body]


def json_response(start_response, body, headers=None):
    headers = [("Content-Type", "application/json; charset=UTF-8")]
    return response(start_response, 200, body=json.dumps(body), headers=headers)


def basic_response(start_response, code, body=""):
    headers = [("Content-Type", "text/plain; charset=UTF-8")]
    return response(start_response, code, body, headers=headers)


class FakeSocket:
    """
    Just enough of the socket interface implemented to do for testing.
    """

    def __init__(self, body):
        super()
        self._body = io.BytesIO(body)

    def makefile(self, mode, bufsize=None):  # noqa: ARG002
        if mode != "rb":
            raise client.UnimplementedFileMode()  # noqa: RSE102
        return self._body


def make_fake_http_response_msg(code=200, body="", headers=None):
    if headers is None:
        headers = []
    elif isinstance(headers, dict):
        headers = list(headers.items())

    msg = client.HTTPMessage()
    msg.set_payload(body)
    msg.add_header("Content-Length", str(len(body)))

    has_content_type = False
    for key, value in headers:
        if key.lower() == "content-type":
            has_content_type = True
        if isinstance(value, tuple) and len(value) == 2:
            value, params = value
            msg.add_header(key, value, **params)
        else:
            msg.add_header(key, value)
    if not has_content_type:
        msg.add_header("Content-Type", "application/octet-stream")
    status = f"HTTP/1.0 {code} {client.responses[code]}\r\n"
    return status.encode("UTF-8") + msg.as_bytes()


def make_fake_http_response(code=200, body="", headers=None):
    sock = FakeSocket(make_fake_http_response_msg(code, body, headers))
    res = client.HTTPResponse(sock)  # type: ignore
    res.begin()
    return res
