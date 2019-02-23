"""
Test utilities for creating WSGI fixtures for testing HTTP clients.
"""

import contextlib
import http.client
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
def fixture(app, returns_app=False):
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
        raise RuntimeError("%s didn't start" % str(app))

    try:
        yield "http://%s:%s/" % queue.get(timeout=5)
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
    assert environ["CONTENT_TYPE"] == "application/json"
    return json.loads(read_body(environ))


def extract_environment(environ):
    non_http = [
        "CONTENT_LENGTH",
        "CONTENT_TYPE",
        "PATH_INFO",
        "QUERY_STRING",
        "REQUEST_METHOD",
    ]
    return dict(
        (key, value)
        for key, value in environ.items()
        if key in non_http or key.startswith("HTTP_")
    )


def json_response(start_response, response, headers=None):
    if headers is None:
        headers = []
    serialised = json.dumps(response)
    start_response(
        "200 OK",
        [
            ("Content-Length", str(len(serialised))),
            ("Content-Type", "application/json; charset=UTF-8"),
        ]
        + headers,
    )
    return [serialised]


def basic_response(start_response, code, body=""):
    start_response(
        "%d %s" % (code, http.client.responses[code]),
        [
            ("Content-Length", str(len(body))),
            ("Content-Type", "text/plain; charset=UTF-8"),
        ],
    )
    return [body]
