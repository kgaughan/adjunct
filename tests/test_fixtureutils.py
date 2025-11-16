import io
import json
import urllib.request

import pytest

from adjunct import fixtureutils


def test_make_fake_http_response_msg():
    msg = fixtureutils.make_fake_http_response_msg(
        code=404,
        body="Not Found",
        headers={"Content-Type": "text/plain"},
    )
    assert msg == b"HTTP/1.0 404 Not Found\r\nContent-Length: 9\nContent-Type: text/plain\n\nNot Found"


def test_make_fake_http_response_msg_complex_header():
    msg = fixtureutils.make_fake_http_response_msg(
        code=404,
        body="Not Found",
        headers={"Content-Type": ("text/plain", {"charset": "UTF-8"})},
    )
    assert msg == b'HTTP/1.0 404 Not Found\r\nContent-Length: 9\nContent-Type: text/plain; charset="UTF-8"\n\nNot Found'


def test_make_fake_http_response_msg_no_content_type():
    msg = fixtureutils.make_fake_http_response_msg(
        code=404,
        body="Not Found",
    )
    assert msg == b"HTTP/1.0 404 Not Found\r\nContent-Length: 9\nContent-Type: application/octet-stream\n\nNot Found"


def test_make_fake_http_response():
    response = fixtureutils.make_fake_http_response(
        body="Hello, World!",
        code=200,
        headers={
            "Content-Type": "text/plain",
            "X-Custom-Header": "CustomValue",
        },
    )
    assert response.status == 200
    assert response.getheader("Content-Type") == "text/plain"
    assert response.getheader("X-Custom-Header") == "CustomValue"
    assert response.read() == b"Hello, World!"


def test_json_response():
    response_status = ""
    response_headers = []

    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    result = fixtureutils.json_response(start_response, {"key": "value"})

    assert response_status.startswith("200")
    headers_dict = dict(response_headers)
    assert headers_dict["Content-Type"] == "application/json; charset=UTF-8"
    assert b"".join(result) == b'{"key": "value"}'


def fixture_app(environ, start_response):  # noqa: ARG001
    """
    A simple WSGI application for testing purposes.
    """
    status = "200 OK"
    headers = [("Content-Type", "text/plain; charset=UTF-8")]
    start_response(status, headers)
    return [b"Fixture App Response"]


def test_fixture():
    with fixtureutils.fixture(fixture_app) as addr, urllib.request.urlopen(addr) as resp:
        body = resp.read()
        assert resp.status == 200
        assert resp.getheader("Content-Type") == "text/plain; charset=UTF-8"
        assert body == b"Fixture App Response"


def test_extract_environment():
    env = {
        "CONTENT_LENGTH": 50,
        "CONTENT_TYPE": "text/plain",
        "PATH_INFO": "/foo/bar",
        "QUERY_STRING": "?foo=bar",
        "REQUEST_METHOD": "GET",
        "PATH": "/bin:/usr/bin",
        "LETS_NOT_LEAK_THIS": "SEKRIT",
        "HTTP_ACCEPT": "text/html",
    }
    extracted = fixtureutils.extract_environment(env)
    assert set(extracted.keys()) == {
        "CONTENT_TYPE",
        "CONTENT_LENGTH",
        "PATH_INFO",
        "QUERY_STRING",
        "REQUEST_METHOD",
        "HTTP_ACCEPT",
    }


def test_read_json_bad_content_type():
    env = {"CONTENT_TYPE": "text/plain"}
    assert fixtureutils.read_json(env) is None


def test_read_json():
    payload = b'{"foo": "bar"}'
    env = {
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": len(payload),
        "wsgi.input": io.BytesIO(payload),
    }
    assert fixtureutils.read_json(env) == {"foo": "bar"}


def test_read_json_no_length():
    payload = b'{"foo": "bar"}'
    env = {
        "CONTENT_TYPE": "application/json",
        "wsgi.input": io.BytesIO(payload),
    }
    assert fixtureutils.read_json(env) == {"foo": "bar"}


def test_read_json_malformed_json():
    env = {
        "CONTENT_TYPE": "application/json",
        "wsgi.input": io.BytesIO(b'{"key": "value",}'),  # Malformed JSON (trailing comma)
    }
    with pytest.raises(json.JSONDecodeError):
        fixtureutils.read_json(env)
