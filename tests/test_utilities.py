import base64

import pytest

from swiss_knife.utilities import (
    convert_keys_to_camel_case,
    decode_base64_text,
    delete_if_present,
    get_env_bool,
    get_env_float,
    get_env_int,
    get_or_default,
    has_value,
    is_empty,
    is_false,
    is_http_status_code,
    is_not_empty,
    is_numeric,
    is_true,
    is_uuid,
    parse_bool,
    sanitize_header_name,
    sanitize_metric_name,
    to_camel_case,
)


def test_empty_checks():
    assert is_empty(None)
    assert is_empty("")
    assert is_empty(" false ")
    assert is_not_empty("value")
    assert not is_not_empty(0)
    assert not is_not_empty(float("inf"))


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("YES", True),
        ("1", True),
        ("false", False),
        ("off", False),
        ("0", False),
    ],
)
def test_parse_bool_known_values(value, expected):
    assert parse_bool(value) is expected


def test_parse_bool_default():
    assert parse_bool("maybe") is None
    assert parse_bool("maybe", default=True) is True


def test_true_false_helpers():
    assert is_true("yes")
    assert not is_true("no")
    assert is_false("no")
    assert not is_false("yes")


@pytest.mark.parametrize(
    "value",
    ["10", "10.5", "-2", "1e3", 5, 5.0, " 7 "],
)
def test_is_numeric_true(value):
    assert is_numeric(value)


@pytest.mark.parametrize("value", ["1.2.3", "abc", "", None, float("nan")])
def test_is_numeric_false(value):
    assert not is_numeric(value)


def test_env_helpers(monkeypatch):
    monkeypatch.setenv("TEST_INT", "12")
    monkeypatch.setenv("TEST_FLOAT", "3.5")
    monkeypatch.setenv("TEST_BOOL", "yes")

    assert get_env_int("TEST_INT") == 12
    assert get_env_float("TEST_FLOAT") == 3.5
    assert get_env_bool("TEST_BOOL") is True
    assert get_env_int("MISSING_INT", default=7) == 7


def test_mapping_helpers():
    data = {"name": "alice", "empty": "", "zero": 0}

    assert has_value(data, "name")
    assert not has_value(data, "empty")
    assert get_or_default(data, "name", "fallback") == "alice"
    assert get_or_default(data, "missing", "fallback") == "fallback"

    delete_if_present(data, "name")
    assert "name" not in data


def test_camel_case_helpers():
    payload = {
        "first_name": "alice",
        "child_items": [{"created_at": "today"}],
    }

    assert to_camel_case("first_name") == "firstName"
    assert convert_keys_to_camel_case(payload) == {
        "firstName": "alice",
        "childItems": [{"createdAt": "today"}],
    }


def test_sanitizers():
    assert sanitize_metric_name("http.requests-total") == "http_requests_total"
    assert sanitize_header_name("x-custom-header") == "X-Custom-Header"


def test_base64_decode():
    encoded = base64.b64encode(b"hello world")
    assert decode_base64_text(encoded) == "hello world"


def test_uuid_helpers():
    assert is_uuid("550e8400-e29b-41d4-a716-446655440000")
    assert is_uuid("550e8400-e29b-41d4-a716-446655440000", version=4)
    assert not is_uuid("not-a-uuid")
    assert not is_uuid("550e8400-e29b-11d4-a716-446655440000", version=4)


@pytest.mark.parametrize(
    "status_code, expected",
    [
        ("200", True),
        ("2**", True),
        ("5**", True),
        ("099", False),
        ("600", False),
        ("20*", False),
    ],
)
def test_http_status_codes(status_code, expected):
    assert is_http_status_code(status_code) is expected
