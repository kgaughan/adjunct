import io
import json
import logging

from adjunct import slog


def get_logger(name: str) -> tuple[io.StringIO, logging.Logger]:
    stream = io.StringIO()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream)
    slog.JSONFormatter.configure_handler(handler)
    logger.addHandler(handler)
    return stream, logger


def test_structured_message_logging():
    stream, logger = get_logger("structured_message_logger")

    logger.info(slog.M("Test message", user="alice", action="login"))

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "Test message"
    assert log_record["user"] == "alice"
    assert log_record["action"] == "login"
    assert "spanId" in log_record


def test_span_metadata_in_logging():
    stream, logger = get_logger("span_metadata_logger")

    with slog.span(request_id="12345", user_id="alice"):
        logger.info(slog.M("User action", action="update_profile"))

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "User action"
    assert log_record["action"] == "update_profile"
    assert log_record["request_id"] == "12345"
    assert log_record["user_id"] == "alice"


def test_nested_spans_logging():
    stream, logger = get_logger("nested_spans_logger")

    with slog.span(request_id="12345"):
        logger.info(slog.M("Outer span message"))
        with slog.span(user_id="alice"):
            logger.info(slog.M("Nested span message", action="delete_account"))
        logger.info(slog.M("Outer span message after nested"))

    log_output = stream.getvalue().strip()
    log_lines = log_output.splitlines()
    outer_log_record = json.loads(log_lines[0])
    nested_log_record = json.loads(log_lines[1])
    after_nested_log_record = json.loads(log_lines[2])

    assert outer_log_record["message"] == "Outer span message"
    assert outer_log_record["request_id"] == "12345"
    assert "user_id" not in outer_log_record

    assert nested_log_record["message"] == "Nested span message"
    assert nested_log_record["request_id"] == "12345"
    assert nested_log_record["user_id"] == "alice"
    assert nested_log_record["action"] == "delete_account"

    assert outer_log_record["spanId"] != nested_log_record["spanId"]
    assert nested_log_record["parentSpanId"] == outer_log_record["spanId"]

    assert after_nested_log_record["message"] == "Outer span message after nested"
    assert after_nested_log_record["request_id"] == "12345"
    assert "user_id" not in after_nested_log_record  # no leakage from nested span
    assert after_nested_log_record["spanId"] == outer_log_record["spanId"]


def test_exception_logging():
    stream, logger = get_logger("exception_logger")

    try:
        raise KeyError("Test exception")  # noqa: TRY301
    except KeyError:
        logger.exception("Something went wrong")

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "Something went wrong"
    assert "exception" in log_record
    assert "KeyError" in log_record["exception"]


def test_plain_message_logging():
    stream, logger = get_logger("plain_message_logger")

    logger.info("A plain log message")

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "A plain log message"


def test_plain_message_with_span():
    stream, logger = get_logger("plain_message_with_span_logger")

    with slog.span(session_id="sess-001"):
        logger.info("A plain log message within a span")

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "A plain log message within a span"
    assert log_record["session_id"] == "sess-001"


def test_structured_message_without_jsonformatter():
    logger = logging.getLogger("plain_logger")
    logger.setLevel(logging.DEBUG)
    stream = io.StringIO()
    logger.addHandler(logging.StreamHandler(stream))

    logger.info(slog.M("Test message without JSONFormatter", key="value"))
    log_output = stream.getvalue().strip()

    assert "Test message without JSONFormatter" in log_output
    assert '"key": "value"' in log_output


def test_m_without_metadata():
    m = slog.M("Simple message")
    assert str(m) == "Simple message"


def test_m_with_metadata():
    m1 = slog.M("Outer message with metadata", user="bob", action="view")
    log_str = str(m1)
    assert log_str.startswith("Outer message with metadata | ")
    _, json_part = log_str.split(" | ", 1)
    m1_data = json.loads(json_part)
    assert len(m1_data) == 3
    assert m1_data["user"] == "bob"
    assert m1_data["action"] == "view"
    print(m1_data)
    assert "spanId" in m1_data
    assert "parentSpanId" not in m1_data

    with slog.span(request_id="abc123"):
        m2 = slog.M("Message with metadata", user="bob")
        log_str = str(m2)
    assert log_str.startswith("Message with metadata | ")
    _, json_part = log_str.split(" | ", 1)
    m2_data = json.loads(json_part)
    assert len(m2_data) == 4
    assert m2_data["request_id"] == "abc123"
    assert m2_data["user"] == "bob"
    assert m2_data["spanId"] != m1_data["spanId"]
    assert m2_data["parentSpanId"] == m1_data["spanId"]
