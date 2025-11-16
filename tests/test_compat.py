from adjunct import compat


def test_parse_header():
    header = "text/html"
    key, params = compat.parse_header(header)
    assert key == "text/html"
    assert params == {}

    header = "text/html;"
    key, params = compat.parse_header(header)
    assert key == "text/html"
    assert params == {}

    header = 'application/json; version=1.0; format="pretty"'
    key, params = compat.parse_header(header)
    assert key == "application/json"
    assert params == {"version": "1.0", "format": "pretty"}

    header = "multipart/form-data; boundary=----WebKitFormBoundary"
    key, params = compat.parse_header(header)
    assert key == "multipart/form-data"
    assert params == {"boundary": "----WebKitFormBoundary"}
