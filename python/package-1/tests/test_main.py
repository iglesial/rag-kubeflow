"""Tests for main module."""

from package_1 import process_data


def test_process_data() -> None:
    """Test that process_data adds processed flag."""
    input_data = [{"id": 1, "value": "test"}]
    result = process_data(input_data)

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["processed"] is True
    assert result[0]["value"] == "test"


def test_process_data_empty() -> None:
    """Test that process_data handles empty input."""
    result = process_data([])
    assert result == []


def test_process_data_multiple() -> None:
    """Test that process_data handles multiple records."""
    input_data = [{"id": i, "value": f"val_{i}"} for i in range(5)]
    result = process_data(input_data)

    assert len(result) == 5
    assert all(item["processed"] is True for item in result)
