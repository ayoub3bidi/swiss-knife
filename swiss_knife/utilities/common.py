import base64
import math
import os
import re
import uuid
from typing import Any, Mapping, MutableMapping, Optional, Union

_EMPTY_STRINGS = {"", "null", "nil", "none", "undef", "undefined", "false"}
_TRUE_STRINGS = {"true", "ok", "yes", "on", "1"}
_FALSE_STRINGS = {"false", "ko", "no", "off", "0"}
_HTTP_STATUS_WILDCARD = re.compile(r"^[1-5]\*\*$")
_ALLOWED_CHARS_METRIC_PATTERN = re.compile(r"[^a-zA-Z0-9]")


def _normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip()
    return text


def is_not_empty(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return False
        return value != 0
    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return len(value) > 0

    text = _normalize_text(value)
    if text is None:
        return False
    return text.lower() not in _EMPTY_STRINGS


def is_empty(value: Any) -> bool:
    return not is_not_empty(value)


def parse_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    if isinstance(value, bool):
        return value

    text = _normalize_text(value)
    if text is None or text == "":
        return default

    lowered = text.lower()
    if lowered in _TRUE_STRINGS:
        return True
    if lowered in _FALSE_STRINGS:
        return False
    return default


def is_true(value: Any) -> bool:
    result = parse_bool(value, default=False)
    return bool(result)


def is_false(value: Any) -> bool:
    result = parse_bool(value, default=True)
    return result is False


def is_numeric(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return not (isinstance(value, float) and not math.isfinite(value))

    text = _normalize_text(value)
    if text is None or text == "":
        return False

    try:
        number = float(text)
    except ValueError:
        return False
    return math.isfinite(number)


def get_env_int(var_name: str, default: Optional[int] = None) -> Optional[int]:
    value = os.getenv(var_name)
    text = _normalize_text(value)
    if text is not None:
        try:
            return int(text)
        except ValueError:
            return default
    return default


def get_env_float(var_name: str, default: Optional[float] = None) -> Optional[float]:
    value = os.getenv(var_name)
    if is_numeric(value):
        return float(str(value).strip())
    return default


def get_env_bool(var_name: str, default: Optional[bool] = None) -> Optional[bool]:
    return parse_bool(os.getenv(var_name), default=default)


def has_value(mapping: Optional[Mapping[str, Any]], key: str) -> bool:
    if mapping is None:
        return False
    return key in mapping and is_not_empty(mapping[key])


def get_or_default(
    mapping: Optional[Mapping[str, Any]],
    key: str,
    default: Any,
) -> Any:
    if not has_value(mapping, key):
        return default
    assert mapping is not None
    return mapping[key]


def delete_if_present(mapping: Optional[MutableMapping[str, Any]], key: str) -> None:
    if mapping is not None and has_value(mapping, key):
        del mapping[key]


def to_camel_case(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name
    return "".join(part.title() if index else part for index, part in enumerate(parts))


def convert_keys_to_camel_case(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            to_camel_case(str(key)): convert_keys_to_camel_case(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    return data


def sanitize_metric_name(name: str) -> str:
    return re.sub(_ALLOWED_CHARS_METRIC_PATTERN, "_", name)


def sanitize_header_name(name: str) -> str:
    return "-".join(word.capitalize() for word in name.split("-"))


def decode_base64_text(encoded_data: Union[str, bytes]) -> str:
    decoded_content = base64.b64decode(encoded_data, validate=True)
    return decoded_content.decode("utf-8")


def is_uuid(value: Any, version: Optional[int] = None) -> bool:
    text = _normalize_text(value)
    if text is None or text == "":
        return False

    try:
        parsed = uuid.UUID(text)
    except (ValueError, AttributeError, TypeError):
        return False

    return version is None or parsed.version == version


def is_http_status_code(status_code: Any) -> bool:
    if isinstance(status_code, int):
        return 100 <= status_code <= 599

    text = _normalize_text(status_code)
    if text is None or text == "":
        return False

    if _HTTP_STATUS_WILDCARD.match(text):
        return True

    if len(text) != 3 or not text.isdigit():
        return False

    code = int(text)
    return 100 <= code <= 599
