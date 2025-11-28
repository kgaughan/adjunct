import io
import json
import logging

from adjunct import slog


def test_structured_message_logging():
    stream = io.StringIO()
    logger = slog.get_logger("test_logger", level=logging.DEBUG, handler=logging.StreamHandler(stream))

    logger.info(slog.M("Test message", user="alice", action="login"))

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "Test message"
    assert log_record["user"] == "alice"
    assert log_record["action"] == "login"
    assert "spanId" in log_record


def test_span_metadata_in_logging():
    stream = io.StringIO()
    logger = slog.get_logger("test_logger", level=logging.DEBUG, handler=logging.StreamHandler(stream))

    with slog.span(request_id="12345", user_id="alice"):
        logger.info(slog.M("User action", action="update_profile"))

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "User action"
    assert log_record["action"] == "update_profile"
    assert log_record["request_id"] == "12345"
    assert log_record["user_id"] == "alice"


def test_nested_spans_logging():
    stream = io.StringIO()
    logger = slog.get_logger("test_logger", level=logging.DEBUG, handler=logging.StreamHandler(stream))

    with slog.span(request_id="12345"):
        logger.info(slog.M("Outer span message"))
        with slog.span(user_id="alice"):
            logger.info(slog.M("Nested span message", action="delete_account"))

    log_output = stream.getvalue().strip()
    log_lines = log_output.splitlines()
    outer_log_record = json.loads(log_lines[0])
    nested_log_record = json.loads(log_lines[1])

    assert outer_log_record["message"] == "Outer span message"
    assert outer_log_record["request_id"] == "12345"
    assert "user_id" not in outer_log_record

    assert nested_log_record["message"] == "Nested span message"
    assert nested_log_record["request_id"] == "12345"
    assert nested_log_record["user_id"] == "alice"
    assert nested_log_record["action"] == "delete_account"

    assert outer_log_record["spanId"] != nested_log_record["spanId"]


def test_exception_logging():
    stream = io.StringIO()
    logger = slog.get_logger("test_logger", level=logging.DEBUG, handler=logging.StreamHandler(stream))

    try:
        raise KeyError("Test exception")
    except:
        logger.exception("Something went wrong")

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "Something went wrong"
    assert "exception" in log_record
    assert "KeyError" in log_record["exception"]


def test_plain_message_logging():
    stream = io.StringIO()
    logger = slog.get_logger("test_logger", level=logging.DEBUG, handler=logging.StreamHandler(stream))

    logger.info("A plain log message")

    log_output = stream.getvalue().strip()
    log_record = json.loads(log_output)

    assert log_record["message"] == "A plain log message"


def test_structured_message_without_jsonformatter():
    logger = logging.getLogger("plain_logger")
    logger.setLevel(logging.DEBUG)
    stream = io.StringIO()
    logger.addHandler(logging.StreamHandler(stream))

    logger.info(slog.M("Test message without JSONFormatter", key="value"))
    log_output = stream.getvalue().strip()

    assert "Test message without JSONFormatter" in log_output
    assert '"key": "value"' in log_output
