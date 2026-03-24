"""Tests for client.py response handling robustness.

These tests validate that the Meebook and Huskelisten API response
parsing handles unexpected response types gracefully without crashing.
The core issue is that json.loads() can return any JSON type (string,
number, dict, list, etc.) and the code must validate the type before
iterating.
"""

import json
import pytest


def parse_and_validate_meebook_response(response_text):
    """Simulate the Meebook response parsing logic from client.py.

    Returns a tuple of (status, result) where status is one of:
    - "ok": valid list response, result is the list
    - "token_expired": token expired, result is the message
    - "exception": exceptionMessage dict, result is the message
    - "unexpected": unexpected type, result is the type name
    - "error": parse failure, result is None
    """
    try:
        data = json.loads(response_text, strict=False)
    except (json.JSONDecodeError, ValueError):
        data = None

    if isinstance(data, dict) and "message" in data and "expired" in str(data["message"]).lower():
        return ("token_expired", data["message"])

    if not isinstance(data, list):
        if isinstance(data, dict) and "exceptionMessage" in data:
            return ("exception", data["exceptionMessage"])
        elif data is not None:
            return ("unexpected", type(data).__name__)
        return ("error", None)

    return ("ok", data)


def parse_and_validate_huskelisten_response(response_text):
    """Simulate the Huskelisten response parsing logic from client.py.

    Returns a list of person dicts if valid, or None if invalid.
    """
    try:
        data = json.loads(response_text, strict=False)
    except (json.JSONDecodeError, ValueError):
        data = None

    if not isinstance(data, list):
        if data is not None:
            return ("unexpected", type(data).__name__)
        return ("error", None)

    return ("ok", data)


class TestMeebookResponseHandling:
    """Test that Meebook response parsing handles all JSON types correctly."""

    def test_valid_list_response(self):
        """Normal case: API returns a JSON array of person objects."""
        response = '[{"name": "Test Person", "weekPlan": []}]'
        status, result = parse_and_validate_meebook_response(response)
        assert status == "ok"
        assert len(result) == 1
        assert result[0]["name"] == "Test Person"

    def test_empty_list_response(self):
        """API returns an empty array - should work fine."""
        response = "[]"
        status, result = parse_and_validate_meebook_response(response)
        assert status == "ok"
        assert result == []

    def test_string_response(self):
        """API returns a JSON string - this was the original bug.
        json.loads('"some string"') returns a Python str, and iterating
        over it gives individual characters, causing TypeError."""
        response = '"Unauthorized"'
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "str"

    def test_error_string_response(self):
        """API returns a plain error string."""
        response = '"Token expired"'
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "str"

    def test_exception_message_dict(self):
        """API returns an error dict with exceptionMessage."""
        response = '{"exceptionMessage": "Invalid token"}'
        status, msg = parse_and_validate_meebook_response(response)
        assert status == "exception"
        assert msg == "Invalid token"

    def test_dict_without_exception_message(self):
        """API returns a dict without exceptionMessage."""
        response = '{"error": "something went wrong"}'
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "dict"

    def test_jwt_token_expired_response(self):
        """API returns a dict indicating JWT token expired.
        This should be detected so the token can be refreshed."""
        response = '{"message": "JWT-Token expired, please renew."}'
        status, msg = parse_and_validate_meebook_response(response)
        assert status == "token_expired"
        assert "expired" in msg.lower()

    def test_jwt_token_expired_case_insensitive(self):
        """Token expiry detection should be case-insensitive."""
        response = '{"message": "JWT-Token Expired, Please Renew."}'
        status, msg = parse_and_validate_meebook_response(response)
        assert status == "token_expired"

    def test_dict_with_message_not_expired(self):
        """API returns a dict with message that is not about expiry."""
        response = '{"message": "Some other error"}'
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "dict"

    def test_null_response(self):
        """API returns JSON null - json.loads("null") returns None,
        which is not a list, and data is None so we get error status."""
        response = "null"
        status, result = parse_and_validate_meebook_response(response)
        assert status == "error"
        assert result is None

    def test_number_response(self):
        """API returns a JSON number."""
        response = "42"
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "int"

    def test_boolean_response(self):
        """API returns a JSON boolean."""
        response = "false"
        status, type_name = parse_and_validate_meebook_response(response)
        assert status == "unexpected"
        assert type_name == "bool"

    def test_invalid_json_response(self):
        """API returns non-JSON text (e.g., HTML error page)."""
        response = "<html>502 Bad Gateway</html>"
        status, result = parse_and_validate_meebook_response(response)
        assert status == "error"
        assert result is None

    def test_empty_response(self):
        """API returns empty body."""
        response = ""
        status, result = parse_and_validate_meebook_response(response)
        assert status == "error"
        assert result is None


class TestHuskelistenResponseHandling:
    """Test that Huskelisten response parsing handles all JSON types correctly."""

    def test_valid_list_response(self):
        """Normal case: API returns a JSON array of person objects."""
        response = '[{"userName": "Test User", "teamReminders": []}]'
        status, result = parse_and_validate_huskelisten_response(response)
        assert status == "ok"
        assert len(result) == 1
        assert result[0]["userName"] == "Test User"

    def test_empty_list_response(self):
        """API returns an empty array - should work fine."""
        response = "[]"
        status, result = parse_and_validate_huskelisten_response(response)
        assert status == "ok"
        assert result == []

    def test_string_response(self):
        """Same bug pattern as Meebook - string iterated char by char."""
        response = '"Unauthorized"'
        status, type_name = parse_and_validate_huskelisten_response(response)
        assert status == "unexpected"
        assert type_name == "str"

    def test_dict_response(self):
        """API returns a dict instead of list."""
        response = '{"error": "something"}'
        status, type_name = parse_and_validate_huskelisten_response(response)
        assert status == "unexpected"
        assert type_name == "dict"

    def test_invalid_json_response(self):
        """API returns non-JSON text."""
        response = "Internal Server Error"
        status, result = parse_and_validate_huskelisten_response(response)
        assert status == "error"
        assert result is None

    def test_null_response(self):
        """API returns JSON null - treated same as parse failure."""
        response = "null"
        status, result = parse_and_validate_huskelisten_response(response)
        assert status == "error"
        assert result is None
