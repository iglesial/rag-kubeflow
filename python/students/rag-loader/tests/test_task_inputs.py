"""Tests for rag-loader task inputs."""

import pytest

from rag_loader.task_inputs import TaskInputs, task_inputs


def test_task_inputs_defaults() -> None:
    """Test that TaskInputs has expected default values."""
    assert task_inputs.input_dir == "../../data/documents"
    assert task_inputs.output_dir == "../../data/chunks"
    assert task_inputs.chunk_size == 512
    assert task_inputs.chunk_overlap == 64


def test_task_inputs_is_instance() -> None:
    """Test that the module-level task_inputs is a TaskInputs instance."""
    assert isinstance(task_inputs, TaskInputs)


def test_inject_document_name_default_false() -> None:
    """Test that inject_document_name defaults to False."""
    assert task_inputs.inject_document_name is False


def test_inject_document_name_can_be_overridden() -> None:
    """Test that inject_document_name can be set to True."""
    inputs = TaskInputs(inject_document_name=True)  # type: ignore[call-arg]
    assert inputs.inject_document_name is True


@pytest.mark.parametrize("value", [True, False])
def test_inject_document_name_is_bool(value: bool) -> None:
    """
    Test that inject_document_name accepts boolean values.

    Parameters
    ----------
    value : bool
        Boolean value to test.
    """
    inputs = TaskInputs(inject_document_name=value)  # type: ignore[call-arg]
    assert isinstance(inputs.inject_document_name, bool)
    assert inputs.inject_document_name == value
