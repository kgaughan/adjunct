import json
import typing as t


def load_json_documents(payloads: str) -> t.Iterator[dict | list]:
    """Load multiple JSON documents from a string.

    Each JSON document is expected to be separated by whitespace or newlines.

    This is useful for processing streams of JSON objects, such as logs or data
    exports, where each line or block represents a separate entity.

    Args:
        payloads: A text stream containing JSON documents.

    Yields:
        Parsed JSON objects/lists.

    Examples:
        >>> json_stream = '''
        ... {"name": "Alice"}
        ... {"name": "Bob"}
        ... [1, 2, 3]
        ... '''
        >>> for doc in load_json_documents(json_stream):
        ...     print(doc)
        {'name': 'Alice'}
        {'name': 'Bob'}
        [1, 2, 3]
    """

    decoder = json.JSONDecoder()
    while True:
        payloads = payloads.lstrip()
        if not payloads:
            break
        obj, idx = decoder.raw_decode(payloads)
        yield obj
        payloads = payloads[idx:]
