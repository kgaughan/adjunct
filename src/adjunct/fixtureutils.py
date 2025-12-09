"""Test utilities for creating [WSGI][] fixtures for testing HTTP clients.

[WSGI]: https://wsgi.readthedocs.io/
"""

from collections import abc
import contextlib
from http import client
import io
import json
import multiprocessing
import typing as t
from wsgiref.simple_server import make_server

# Supporting types for WSGI apps
_start_response = abc.Callable[[str, list[tuple[str, str]]], None]
_app = abc.Callable[[dict[str, t.Any], _start_response], t.Iterable[bytes]]


def _start_server(app, queue, returns_app):  # pragma: no cover
    """Run a fixture application."""
    # This is excluded from coverage as it's only run in a separate process.
    # If there were an issue, the tests using fixtures would fail.
    if returns_app:
        # 'app' is actually a callable that returns an app. Useful when dealing
        # with a app implemented as a class.
        app = app()
    svr = make_server("localhost", 0, app)
    queue.put(("localhost", svr.server_port))
    svr.serve_forever()


@contextlib.contextmanager
def fixture(app: _app, *, returns_app: bool = False, timeout: int = 5) -> abc.Generator[str, None, None]:
    """Spin up a fixture application up in its own process.

    Set `returns_app` if `app` is a callable that returns the actual app (such
    as a class).

    Args:
        app: a WSGI app or a callable that returns a WSGI app
        returns_app: treat `app` as a callable that returns a WSGI app
        timeout: maximum length of time to wait for the app to start

    Yields:
        The URL serving the WSGI application.
    """
    queue: multiprocessing.Queue[tuple[str, int]] = multiprocessing.Queue()

    # Spin up a separate process for our fixture server.
    proc = multiprocessing.Process(target=_start_server, args=(app, queue, returns_app))
    proc.start()
    if proc.exitcode is not None:  # pragma: no cover
        raise RuntimeError(f"{app} didn't start")

    try:
        hostname, port = queue.get(timeout=timeout)
        yield f"http://{hostname}:{port}/"
    finally:
        if proc.exitcode is None:
            proc.terminate()
        queue.close()


def _get_content_length(environ: dict) -> int | None:
    """Get `CONTENT_LENGTH` from the WSGI environment safely."""
    content_length = environ.get("CONTENT_LENGTH")
    return None if content_length is None else int(content_length)


def read_body(environ: dict) -> bytes:
    """Read any input from the WSGI environment."""
    return environ["wsgi.input"].read(_get_content_length(environ))


def read_json(environ: dict):
    """Read a JSON document from the WSGI environment."""
    if environ["CONTENT_TYPE"] == "application/json":
        return json.loads(read_body(environ))
    return None


def extract_environment(environ: dict) -> dict:
    """Extract any CGI environment variable from a dictionary."""
    non_http = [
        "CONTENT_LENGTH",
        "CONTENT_TYPE",
        "PATH_INFO",
        "QUERY_STRING",
        "REQUEST_METHOD",
    ]
    return {key: value for key, value in environ.items() if key in non_http or key.startswith("HTTP_")}


def response(
    start_response: _start_response,
    code: int,
    body: bytes = b"",
    headers: list[tuple[str, str]] | None = None,
) -> t.Iterable[bytes]:
    """Construct a WSGI response.

    Args:
        start_response: a callable implementing the WSGI `start_response` interface
        code: the HTTP status code to use
        body: the body of the response
        headers: any additional headers to send beside `Content-Type`.

    Yields:
        the wrapped body
    """
    if headers is None:
        headers = []
    headers.append(("Content-Length", str(len(body))))
    start_response(f"{code} {client.responses[code]}", headers)
    yield body


def json_response(start_response: _start_response, body) -> t.Iterable[bytes]:
    """Send a JSON document with a "200 OK" status code."""
    headers = [("Content-Type", "application/json; charset=UTF-8")]
    return response(start_response, 200, body=json.dumps(body).encode("utf-8"), headers=headers)


def basic_response(start_response: _start_response, code: int, body: str = "") -> t.Iterable[bytes]:
    """Send a plaintext document.

    Args:
        start_response: a callable implementing the WSGI `start_response` interface
        code: the HTTP status code to use
        body: the body of the response
    """
    headers = [("Content-Type", "text/plain; charset=UTF-8")]
    return response(start_response, code, body.encode("utf-8"), headers=headers)


class _FakeSocket:
    """Just enough of the socket interface implemented to do for testing.

    Args:
        body: a buffer containing the full response message
    """

    def __init__(self, body: bytes):
        super()
        self._body = io.BytesIO(body)

    def makefile(self, mode, bufsize=None):  # noqa: ARG002
        if mode != "rb":  # pragma: no cover
            raise client.UnimplementedFileMode()  # noqa: RSE102
        return self._body


def _make_fake_http_response_msg(
    code: int = 200,
    body: str = "",
    headers: list[tuple[str, t.Any]] | None = None,
) -> bytes:
    """Creates a HTTP message and serialises it as bytes.

    Args:
        code: a HTTP status code
        body: the body of the response
        headers: a list of headers to include

    Returns:
        The serialised HTTP message.
    """
    if headers is None:
        headers = []

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
            msg.add_header(key, value)  # type: ignore
    if not has_content_type:
        msg.add_header("Content-Type", "application/octet-stream")
    status = f"HTTP/1.0 {code} {client.responses[code]}\r\n"
    return status.encode("UTF-8") + msg.as_bytes()


def make_fake_http_response(
    code: int = 200,
    body: str = "",
    headers: list[tuple[str, str]] | None = None,
) -> client.HTTPResponse:
    """Make a fake [http.client.HTTPResponse][] object.

    Args:
        code: HTTP status code
        body: response body
        headers: any headers to include, if any

    Returns:
        A fake response object.
    """
    sock = _FakeSocket(_make_fake_http_response_msg(code, body, headers))
    res = client.HTTPResponse(sock)  # type: ignore
    res.begin()
    return res
