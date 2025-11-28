from adjunct import jsonutils


def test_is_valid_json():
    json_stream = """
    {"name": "Alice"}
    {"name": "Bob"}
    [1, 2, 3]
    """
    expected_outputs = [
        {"name": "Alice"},
        {"name": "Bob"},
        [1, 2, 3],
    ]

    results = list(jsonutils.load_json_documents(json_stream))
    assert results == expected_outputs
